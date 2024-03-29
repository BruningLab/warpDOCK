# warpDOCK
A large-scale virtual drug discovery pipeline optimised for Oracle Cloud Infrastructure.
&nbsp;

If you use warpDOCK, please cite: 
&nbsp;

McDougal, D.P., Rajapaksha, H.R., Pederick, J.P., and Bruning, J.B. warpDOCK: Large-Scale Virtual Drug Discovery Using Cloud Infrastructure, _ACS Omega_, 2023, DOI: https://doi.org/10.1021/acsomega.3c02249
&nbsp;

This documentation covers:

- Setting up a virtual cloud network (VCN) in Oracle Cloud Infrastructure
- Creating the Network File Storage (NFS) server in the VCN and attaching cloud storage devices
- Setting up different computing shapes (CPUs)
- Installing the warpDOCK software
- Description of warpDOCK programs and example implementation
    
&nbsp;
    
**1. Getting started: setting up the Virtual Cloud Network**


_This documentation assumes that you have already set up your tenancy in your home region._

To get started, ensure that you are in the correct region for which you want to create the virtual cloud network (VCN). Changing the region which hosts the VCN later will require setting up from scratch.

&nbsp;

  **1.1. Virtual cloud network**
  
To set up the VCN, from the homepage menu (top left) navigate to the **Networking tab** and select "Virtual Cloud Networks". Here, either manually create a VCN or use the VCN Wizard (recommended). If using the VCN Wizard choose your VCN name and select the your user compartment. For all other options leave as default.

&nbsp;

**1.2. Login host-node**

Within the VCN there are two layers: the public subnet and the private subnet (only accesible from the public subnet). For security, we will only use the login host-node as a lillypad to enter the private subnet. 

&nbsp;

Navigate to the **Compute** tab in the homepage menu and select "Instances" from the options menu. On the left side of the new window, choose your compartment by clicking on the drop-down menu. Next, click on the "Create Instance" button and a new window will appear.

&nbsp;

In OCI, the _shape_ (computer) is launched as an object termed an "Instance", and can be a bare-metal machine, a virtual machine or a GPU - each shape has different characteristics. An _image_ refers to the operating system e.g., Ubuntu. Click on “edit” and then on the “Change image” button, a window will pop up on the right of the screen.

&nbsp;

Under "Platform Images" select Canonical Ubuntu and click on continue. As the host login-node is used only as a lillypad, select the Virtual machine tile and then Ampere as the brand. Under “Shape name” select VM.Standard.A1.Flex (_always free_). Change the number of CPUs to 1 and memory as 6Gb, select continue.

&nbsp;

Next, under the **Networking** tab, select “public subnet” (which will generate a public IP address for the instance).

&nbsp;

Under the **Add SSH keys** tab, generate a key-pair and save, or upload a pre-existing public key. The key file is essential for access to the public and private subnets - so keep it safe!!

&nbsp;

Select “end to end” encryption.

Save and close.

&nbsp;

**1.3. Create the Control-node, launch the NFS server and attach a block volume (the scratch surface)**

_Create a new instance in the **private subnet** called "Control-node" with the Canonical Ubuntu image and the following shape:_

Vm.E4.Flex CPUs = 12 and 32Gb RAM.

Upload the public key file.

SSH into the login host-node and update:

```
ssh -i <path to private key file> ubuntu@<login host-node IP>

sudo apt update
```
From the login host-node, SSH into the Control-node and update:
```
ssh -i <path to private key file> ubuntu@<control node IP>

sudo apt update

exit
```
&nbsp;

_Create a new instance in the **private subnet** called "NFS server", with the Canonical Ubuntu image and the following shape:_

Vm.E4.Flex: 12 OCPUs and 16Gb RAM.

Upload the public key file, save and close.

&nbsp;

From the host login-node SSH into the NFS server, update and install NFS-kernel dependencies:

```
ssh -i <path to private key file> ubuntu@<NFS server IP address>

sudo apt update

sudo apt-get install nfs-kernel-server

exit
```

&nbsp;


_Navigate to the **Networking** tab in the homepage menu, and select the "Virtual Cloud Networks" link._

In your compartment select the VCN you just recently created. In the listed subnets:

o	Select “Private Subnet VCN”

o	Select “security rules"

  - Select “add ingress rules”

    •	Update the source CDIR to source 10.0.0.0/16

    •	Update the destination port range to = 111,2048-2050

    •	Add and exit

  - Select “egress” rules

    •	Update the source CDIR to source 10.0.0.0/16

    •	Update the source port range = 111,2048-2050

    •	Add and exit

Repeat the above for “Public Subnet VCN”.

&nbsp;


_Navigate to **Storage** in the homepage menu and then into Block Volumes:_

Follow the steps to create a block volume. A storage size of up 6-10Tb is appropriate for most ultra-large screens (>100 million ligands) but can be increased or decreased later. Sometimes, the OS will prevent new data being written if capacity reaches ~55%, so be mindful of this when allocating block volume size.

&nbsp;

From the host login-node, SSH into the NFS server and in the home directory enter the following commands into the terminal:

```
sudo mkdir -p /mnt/NFS

cd /mnt

sudo chown ubuntu:ubuntu NFS/

sudo vim /etc/exports
```
Add a new line to the exports file and add:

```
/mnt/NFS *(rw,sync,no_root_squash,no_subtree_check)

:wq
```
Save and close the text editor, then enter the following code chunk into the terminal to open up the ports:
```
sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 111 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 2048 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 2049 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 2050 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 111 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 2048 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 2049 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 2050 -j ACCEPT

sudo netfilter-persistent save

sudo exportfs -a

sudo service nfs-kernel-server restart
```

&nbsp;

**1.4. Block volume and mounting to NFS server**

Navigate to **Storage** in the homepage menu and select "block volumes". Select "Attached Instances" then select "Attach to instance":

- check "read/write"
- select instance: "NFS" (the server you just created)
- select "Attach"
- add filepath for block volume: /dev/oracleoci/oraclevdb

Once the block volume has finished provisioning, select options for attached instance:

- select "iSCI Commands and Information"
- copy "attach" commands

In NFS server, paste and enter the iSCI commands into the terminal. When this is complete, enter the following into the terminal:

```
sudo mkfs.ext4 /dev/oracleoci/oraclevdb

sudo vim /etc/fstab
```

Enter on a new line in the fstab file:

```
/dev/oracleoci/oraclevdb	/mnt/NFS	ext4	_netdev,nofail 0 1

:wq
```
Save and exit the text editor, then enter the following into the terminal:

```
sudo mount -a
```


&nbsp;

**The NFS server (and by virtue block volume) can be mounted to the control node by one of two ways.**

SSH into the Control node. To temporary mount the block volume, enter into the terminal:

```
sudo mount <NFS_IP>:/mnt/NFS /mnt
```
To unmount, enter:

```
sudo unmount /mnt
```

To mount persistently mount the block volume (this is recommended in the private subnet only), enter into the terminal:

```
sudo vim /etc/fstab
```
On a new line, enter:

```
<NFS_IP>:/mnt/NFS	/mnt/NFS nfs defaults	0	1

:wq

sudo mount -a
```

To unmount, simply delete lines from the fstab file and then re-enter "sudo mount -a" command.

&nbsp;

**2. Installing warpDOCK**
&nbsp;

SSH into the Control Node and download the "Installer.sh" script the repository. Make it executable with the command and run:

```
sudo chmod +x Installer.sh

./Installer.sh
```
Running the installer will download the warpDOCK code and Qvina2.1

Ensure that the install worked properly by calling "vina" in the terminal.

&nbsp;


**3. Creating a custom image**

For the creation of compute instances we will first make a clone of the image associated with the Control Node. This will ensure we have all the code and are linked to the NFS server and block volume.

&nbsp;

In the homepage menu, navigate to **Instances** and select the Control Node compute instance. Under the "more options" tab select "create custom image". Follow the prompts and name as "warpDOCK config".

&nbsp;

On the left menu, select "Instance Configurations", and create a custom configuration using the "warpDOCK config" image with 64 OCPUs and 64Gb of RAM in the private subnet. Save and close.
&nbsp;

On the left menu, select "Instance Pool" and create a pool of instances using the custom configuration in the private subnet of the VCN. Here it is important to consider the resources that you will need to perform the screen as the chemical library will be partitioned into sub-folders proportional to the number of instances.

To check that an instance is mounted to the NFS server correctly, SSH into it and enter in the terminal:

```
df -h

lsblk
```
Look to see if the /mnt/NFS file path is mounted to the vdb device. Try navigating to the /mnt/NFS create a directory. Exit the compute instance and find the directory in the Control node.

Now, you are ready to start virtual screening from the Control Node :)

&nbsp;

4. **Usage and examples**
&nbsp;
Here we outline the programs of the warpDOCK pipeline (in the order one would use to perform a large virtual screen).
&nbsp;

**Importing ligand library directly into the VCN from ZINC**

To import directly from ZINC, ensure that the ligand files have 3D coordinates and are in PDBQT format. Save the output as raw URLs and copy into a new .txt in the VCN. An example URL file is:

http://files.docking.org/3D/BC/CARN/BCCARN.xaa.pdbqt.gz

```
ZincDownloader

options:
  -h, --help  show this help message and exit
  -input     [REQUIRED] Path to the URLs.txt document
  -out OUT    [REQUIRED] Output path for multi-PDBQT files
```

&nbsp;

**Splitting each multi-PDBQT file into individual files**

The program "Splitter" is used to process each multi-PDBQT file and strip out the details and coordinates of each ligand, and write to a new file. 

```
Splitter

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR [REQUIRED] Path to multiPDBQT file folder
  -o OUT_DIR, --out_dir OUT_DIR [REQUIRED] Path to output folder
```

&nbsp;

**Dividing the ligand library up into partitions for each instance**

The program "FileDivider" can be used to quickly and easily create new folders and equal number of ligands into each. The number of folders to create is given by a text file containing a list of private IP addresses for each instance, seperated by line.

```
FileDivider

options:
  -h, --help    show this help message and exit
  -input INPUT  Path to PDBQTs for splitting
  -ips IPS      Path to IP list file

```

&nbsp;

**Launching the queue-engine: warpdrive**

The queue-engine can be launched from the control node by calling the Conductor. The s-factor is a value between 1 and 4 which sets the processing threshold limit. Typically, an s-factor of 3 is recommended. Warpdrive can also be impelemented from within a single instance without the need to call the Conductor.

```
Conductor

options:
  -h, --help          show this help message and exit
  -key KEY            Path to the private key
  -path PATH          Path to splinted folders
  -ips IPS            Path to the ip.txt file
  -results RESULTS    Path to results folder
  -logs LOGS          Path to logs folder
  -receptor RECEPTOR  Path to receptor.pdbqt
  -config CONFIG      Path to config file
  -sfactor SFACTOR    Scaling factor
```

**_Once running, if the terminal is closed calculations will stop, and will needed to be restarted. At present, warpDOCK does not include checkpointing but will be addressed in future updates_**

&nbsp;

**Retrieving the results and compiling into a CSV file with maximum and minimum values over a specified number of poses**

The program "FetchResults" is used to scrape through the logs file for each ligand and strip out the binding scores (kcal/mol), and write maximum and minimum values of a range of poses to a CSV file.

```
FetchResults

options:
  -h, --help        show this help message and exit
  -logpath LOGPATH  [REQUIRED] Path to the log file folder
  -nump NUMP        [REQUIRED] Number of dpcking poses
  -out OUT          [REQUIRED] Output CSV file name (*.csv)
```

**Extracting top poses, logs files and library ligand coordinates**

The program "ReDocking" can be used extract a top specified number of files from results, logs and the ligand library based on the CSV generated by "FetchResults" and copy to a new directory.

```
ReDocking

options:
  -h, --help            show this help message and exit
  -i PDBQTFILES         [REQUIRED] Path to the Docking ready PDBQT file folder                   
  -c CSV                [REQUIRED] Path to the CSV file containing summarised docking results
  -n NEWFOLDER          [REQUIRED] Path to the new folder                     
  -t TOP                [REQUIRED] Top selection
```
&nbsp;

For an example, we have provided a small 10K chemical library in 'ready to dock' format, a configuration file and the protein model used in the manuscript. These files are located in the 'example' folder. Before undertaking a very large virtual screen, have a go first using these files to make sure everything is in order (or your own). Depending on the number of instances used, the chemical library will need to be partitioned with FileDivider.py. 
&nbsp;

Enjoy virtual screening. For any issues that arise please contact the Bruning Lab directly.

For best practice in virtual ligand screening, we recommend reading the following _Nature Protocols_ paper by Brian K. Shoichet and colleagues (2021), which can be found here: https://www.nature.com/articles/s41596-021-00597-z

&nbsp;
For technical support using OCI, please contact Oracle directly or use the extensive documentation provided here: https://docs.oracle.com/en/
