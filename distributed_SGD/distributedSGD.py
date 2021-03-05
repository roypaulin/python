import torch
import torch.nn as nn
import torch.nn.functional as F          # adds some efficiency
from torch.utils.data import DataLoader  # lets us load data in batches
from torchvision import datasets, transforms

import torch.distributed as dist
from math import ceil
import time


gbatch_size = 100

# Loss finction
criterion = nn.CrossEntropyLoss()

# Define the model
class MultilayerPerceptron(nn.Module):
    def __init__(self, in_sz=784, out_sz=10, layers=[120,84]):
        super().__init__()
        self.fc1 = nn.Linear(in_sz,layers[0])
        self.fc2 = nn.Linear(layers[0],layers[1])
        self.fc3 = nn.Linear(layers[1],out_sz)
    
    def forward(self,X):
        X = F.relu(self.fc1(X))
        X = F.relu(self.fc2(X))
        X = self.fc3(X)
        return F.log_softmax(X, dim=1)
    
# Count the model parameters   
def count_parameters(model):
    params = [p.numel() for p in model.parameters() if p.requires_grad]
    for item in params:
        print(f'{item:>6}')
    print(f'______\n{sum(params):>6}')
    
    
# Download dataset and Batch loading with DataLoader
def partition_dataset():
    """ Partitioning MNIST """
    transform = transforms.ToTensor()
    dataset = datasets.MNIST(
        './data',
        train=True,
        download=True,
        transform=transform)
    size = dist.get_world_size()
    bsz = int(gbatch_size // float(size))
    train_sampler = torch.utils.data.distributed.DistributedSampler(dataset, size, dist.get_rank())       
    train_set = DataLoader(                                    
        dataset, batch_size=bsz, shuffle=(train_sampler is None), sampler=train_sampler)
    return train_set, bsz

# Test the model
def test(model,rank):
    test_correct = 0
    transform = transforms.ToTensor()
    test_data = datasets.MNIST(
        './data',
        train=False,
        download=True,
        transform=transform)
    
    test_loader = DataLoader(test_data, batch_size=500, shuffle=False)
    
    # Run the testing batches
    with torch.no_grad():
        for b, (X_test, y_test) in enumerate(test_loader):

            # Apply the model
            y_val = model(X_test.view(500, -1))  # Here we flatten X_test

            # Tally the number of correct predictions
            predicted = torch.max(y_val.data, 1)[1] 
            test_correct += (predicted == y_test).sum()
    
    # Print the accuracy on the test set
    print(f'Test accuracy: {test_correct.item()}/{len(test_data)} {test_correct.item()*100/len(test_data):.3f}% rank:{rank}')   
    
# Train the model
def run(rank, world_size):
    
    epochs = 10
    
    torch.manual_seed(101)
    train_set, bsz = partition_dataset()
    model = MultilayerPerceptron()
    start_time = time.time()
    
    sync_initial_weights(model, rank, world_size)
    
    
    optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.85)
    
    num_batches = ceil(len(train_set.dataset) / (float(bsz) * dist.get_world_size()))
    
    model.train()
    for epoch in range(epochs):
        trn_corr = 0
        epoch_loss = 0.0
        for b, (X_train, y_train) in enumerate(train_set):
            b+=1
            
            # Apply the model
            #print(X_train.size())
            sz = X_train.size()[0]
            y_pred = model(X_train.view(sz, -1))  # Here we flatten X_train
            loss = criterion(y_pred, y_train)
            
            epoch_loss += loss.item()
            
            # Tally the number of correct predictions
            predicted = torch.max(y_pred.data, 1)[1]
            batch_corr = (predicted == y_train).sum()
            trn_corr += batch_corr
            
            # Update parameters
            optimizer.zero_grad()
            loss.backward()
            # The all-reduce on gradients
            sync_gradients(model, rank, world_size)

            optimizer.step()
            if b%200==0:
                print(f'epoch: {epoch:2} batch: {b:4} [{sz*b:6}/{60000//world_size}] loss: {loss.item():10.8f} rank: {rank} accuracy: {trn_corr.item()*100/(sz*b):7.3f}%')
            
        print(f'END OF EPOCH: {epoch:2} Loss: {epoch_loss / num_batches:.6f} rank: {rank} Global batch size {gbatch_size} on {world_size} ranks')
        
    print(f'\nDuration: {time.time() - start_time:.0f} seconds') # print the time elapsed
    
    # Test the model
    test(model,rank)
    
    
# Synchronize initial weights among all the replicas  
def sync_initial_weights(model, rank, world_size):
    for param in model.parameters():
        if rank == 0:
            # Rank 0 is sending it's own weight
            # to all it's siblings (1 to world_size)
            for sibling in range(1, world_size):
                dist.send(param.data, dst=sibling)
        else:
            # Siblings must recieve the parameters
            dist.recv(param.data, src=0)

# Sum up all the gradients of all the ranks             
def sync_gradients(model, rank, world_size):
    for param in model.parameters():
        dist.all_reduce(param.grad.data, op=dist.ReduceOp.SUM)            

if __name__ == '__main__':
    dist.init_process_group(backend='mpi')
    size = dist.get_world_size()
    rank = dist.get_rank()
    
    run(rank, size)