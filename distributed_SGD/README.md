# README


run the command below to execute the script:

<b>mpirun -n x python -u distributedSGD.py </b>  
where  <b>x</b> is the number of processes.

The very first time you run it, it will download the dataset. Once the dataset is downloaded, stop the execution (when you see <b>!Done</b>). Now the next times you run the command it will perform the training. If you meet any difficulty, you can download the archive code with the mnist dataset already downloded from <b>https://drive.google.com/file/d/19skHXZsjRguYpY_4VOSF0w2vNZC6UsER/view?usp=sharing</b> 

<b>NB:</b> Unfortunately, PyTorch’s binaries can not include an MPI implementation and we’ll have to recompile it by hand. Fortunately, this process is fairly simple given that upon compilation, PyTorch will look by itself for an available MPI implementation. The following steps install the MPI backend, by installing PyTorch from source. go to <b>https://github.com/pytorch/pytorch#from-source</b>
