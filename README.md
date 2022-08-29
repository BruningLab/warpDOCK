# warpdrive
An ultra-large virtual drug discovery framework optimised for the Oracle Cloud Infrastructure network

&nbsp;

**Getting started**

_The following documentation assusmes that you have set up your tenancy as a federated user are in your correct home region._

&nbsp;

**Setting up the VCN, block volumes, instances and the NFS server**

To get started, first ensure that you are in the correct region for which you want to create the virtual cloud network. Changing the VCN later will require setting up from scratch.

&nbsp;

  **Virtual cloud network**
  
To set up your VCN, from the homepage menu (top left) navigate to the **Networking tab** and select "Virtual Cloud Networks". Either manually create a VCN or use the VCN Wizard (recommended). If using the VCN Wizard choose your VCN name and select the relevant compartment. For all other options leave as default.

&nbsp;

**Bastian login node**

In the VCN there are two layers: the public subnet (accessible from a local server) and the private subnet (accessible from within the public subnet). For security reasons we will first set up a Bastian host node in the public subnet. 

Navigate to the **Compute** tab in the homepage menu and select "Instances" from the options. On the left side of the new window, select the correct compartment by clicking on the drop-down menu and ensure the correct Availability Domain is also checked below. Next, click on the "Create Instance" button and a new window will appear.

For a cloud instance (the computer) An _image_ refers to the operating system e.g., Ubuntu, and _shape_ refers to the hardware. Click on “edit” and then on the “Change image” button, a window will pop up on the right of the screen.


Under "Platform Images" check Canonical Ubuntu and hit continue. The Bastion login node is used only as a lily-pad into the private subnet and simple functions, so select the Virtual machine tile, then Ampere as the brand. Under “Shape name” check VM.Standard.A1.Flex. Change the number of OCPUs as 1 and memory as 6Gb, hit continue.

&nbsp;

Next, under the **Networking** tab, check “private subnet”.

&nbsp;

Under the **Add SSH keys** tab, generate a key-pair and save (this is needed to set up other instances) or upload a pre-existing key.

Check “end to end” encryption.

Save and close.

&nbsp;

**Launch the NFS server and attach a block volume (the scratch surface)**

_Repeat the above steps to create an instance in the private subnet with the Canonical Ubuntu image but change the shape to:_

Shape: Vm.E4.Flex OCPUs (n=12) and 16Gb RAM.

&nbsp;

From your local computer SSH into the Bastian host:

```
ssh -i <path to private key file> ubuntu@<public IP address>
```

If security errors are encountered change permissions:

```
chmod 400 <private key file>
```

Once in the Bastian login node within the public subnet, create a private key file and SSH into the NFS server, then update and install nfs-kernel dependencies:

```
ssh -i <private key file> ubuntu@<NFS server IP address>

sudo apt update

sudo apt-get install nfs-kernerl-server
```

&nbsp;

_Create a new instance in the private subnet called "Control Node" with the Canonical Ubuntu image and the following shape:_

Shape: Vm.E4.Flex OCPUs (n=1) and 32Gb RAM.

SSH into the control node from the Bastian login node and update.

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

Repeat exactly the above for “Public Subnet VCN”.

&nbsp;

_Navigate to Storage in the homepage menu and then into Block Volumes:_

Follow the steps to create a block volume. A storge size of up to 10Tb (>100 million ligands) is appropriate for most ultra-large screens but can be increased later. Sometimes, the OS will prevent new data being written if capacity reaches ~55% so be mindful of this when choosing size.

SSH into the NFS server home directory from the Bastian login node and enter the following commands:

```
sudo mkdir -p /mnt/NFS

cd /mnt

sudo chown ubuntu:ubuntu NFS/

sudo vim /etc/exports
```
Add a new line and enter:

```
/mnt/NFS * (rw, sync, no_root_squash, no_subtree_check)

:wq
```
Save and close, then execute then enter following commands to open up the ports:

```
sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 111 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 2048 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 2049 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p tcp --destination-port 2050 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 111 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 2048 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 2049 -j ACCEPT

sudo iptables -I INPUT -m state --state NEW -p udp --destination-port 2050 -j ACCEPT

sudo netfilter -persistent save

sudo exportfs -a

sudo service nfs-kernel-server restart
```

&nbsp;

**To mount the block volume to the NFS server**

Navigate to **Storage** in the homepage menu and select "block volumes". Select "Attached Instances" then select "Attach to instance":

- check "read/write"
- select instance: "NFS" (the server you just created)
- select "Attach"

Select options for attached instance:

- select "iSCI Commands and Information"
- copy "attach" commands

In NFS server, paste and enter the iSCI commands.

Next, enter the following:

```
sudo mkfs.ext4 /dev/oracleoci/oraclevdb

sudo vim /etc/fstab
```

Enter on a new line in the fstab file:

```
/dev/oracleoci/oraclevdb	/mnt/NFS	ext4	_netdev,nofail 0 1

:wq
```
Save and exit, then enter:

```
sudo mount -a
```
&nbsp;

**The NFS server (and by virtue block volume) can be mounted to the control node by one of two ways.**

SSH into the Control node. To temporary mount the block volume, enter:

```
sudo mount <NFS_IP>:/mnt/NFS /mnt
```
To unmount, enter:

```
sudo unmount /mnt
```

To mount persistently moun the block volume (recommended in the private subnet only), enter:

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

**Now, we will create a custom image with all the programs and dependencies**

Launch an instance in the private subnet called "config" with the Canonical ubuntu image and the following shape:

Shape: Vm.E4.Flex OCPUs (n=64) and 64Gb RAM.

SSH into the new instance and update.

Next, download the source code for Qvina2:

```
wget https://github.com/QVina/qvina/blob/master/bin/qvina2.1
```
Extact the contents and place in /usr/local/bin.

Check that the install works correctly by entering "vina -h" in the terminal.

Cd into /mnt and create the "NFS" directory. Using the instructions above, persistently mount the NFS server to the /mnt/NFS path.

&nbsp;

Warpdrive, installed with pip via:

```
pip install warpdrive
```
Or as source-code from the GitHub repository. If so,  navigate to the home directory of the new instance and enter the following:

```
mkdir -p warpdrive

sudo chown ubuntu:ubuntu warpdrive/

cd warpdrive/

vim warpdrive.py    # copy in the warpdrive code

:wq

chmod +x warpdrive.py

sudo ln -s /home/warpdrive/warpdrive.py /usr/local/bin/warpdrive
```
Check that the install works by entering "warpdrive -h" into the terminal and then exit the compute instance.

&nbsp;

SSH into the Control Node and **repeat the exact steps as above** but name the directory "Conductor" and create the conductor.py script.

Exit the Control Node.

&nbsp;

In the homepage menu, navigate to instances and select the "config" compute instance. Under the "more options" tab select "create custom image". Follow the prompts and name as "warpdrive".

On the left menu, select "Instance Configurations", and create a custom configuration using the warpdrive image with 64 OCPUs and 64Gb of RAM in the private subnet. Save and close.

On the left menu, select "Instance Pool" and create a pool of instances using the custom configuration in the private subnet of the VCN.

To check that everything works, SSH into one of the new instances and enter:

```
df -h

lsblk
```
Look to see if the /mnt/NFS file path is mounted to the vdb device. Try navigating to the /mnt/NFS create a directory. Exit the compute instance and find the directory in the Control node.

Now, you are ready to start virtual screening. 

&nbsp;
&nbsp;

# Usage and examples

&nbsp;

**Importing a ligand library directly into the VCN from ZINC**

To import directly from ZINC, ensure that the ligand files have 3D coordinates and are in PDBQT format. Save the output as raw URLs and copy into a new .txt in the VCN. An example URL file is:

http://files.docking.org/3D/BC/CARN/BCCARN.xaa.pdbqt.gz

```
./Downloader.py

options:
  -h, --help  show this help message and exit
  -urls URLS  [REQUIRED] Path to the URLs.txt document
  -out OUT    [REQUIRED] Output path for multi-PDBQT files
```

The contents of each URL can be downloaded using the program "FileDivider.py" into a new folder. Whilst in PDBQT format, each file will have hundreds to thousands of ligand coordinates.

&nbsp;

**Splitting each multi-PDBQT file into individual files**

The program "Splitter.py" is used to process each multi-PDBQT file and strip out the details and coordinates of each ligand, and write to a new file. 

```
./Splitter.py

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR [REQUIRED] Path to multiPDBQT file folder
  -o OUT_DIR, --out_dir OUT_DIR [REQUIRED] Path to output folder
```

&nbsp;

**Dividing the ligand library up into batches for each instance**

The program "FileDivider.py" can be used to quickly and easily create new folders and equal number of ligands into each. The number of folders to create is given by a text file containing a list of private IP addresses for each instance, seperated by new lines.

```
./FileDivider.py

options:
  -h, --help    show this help message and exit
  -input INPUT  Path to PDBQTs for splitting
  -ips IPS      Path to IP list file

```

&nbsp;

**Launching the queue-engine**

When all instances are booted up and running, the queue-engine can be launched from the control node by calling the conductor. The sfactor is a value between 1 and 4 which sets the processing threshold.

```
conductor

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

**_Once running, if the terminal is closed calculations will stop, and will needed to be restarted_**

&nbsp;

**Retrieving the results and compiling into a CSV file with maximum and minimum values over a specified number of poses**

The program "FetchResults.py" is used to scrape through the logs file for each ligand and strip out the binding scores (kcal/mol) and write maximum and minimum values to a CSV file. The number of poses refers to the range e.g., the top pose and the next 3 poses.

```
./FetchResults.py

options:
  -h, --help        show this help message and exit
  -logpath LOGPATH  [REQUIRED] Path to the log file folder
  -nump NUMP        [REQUIRED] Number of dpcking poses
  -out OUT          [REQUIRED] Output CSV file name (*.csv)
```

**Extracting top poses, logs files and library ligand coordinates**

The program "ReDocking.py" can be used extract a top specified number of files from results, logs and the ligand library based on the CSV generated by FetchResults.py and copy to a new directory.

```
./ReDocking.py

options:
  -h, --help            show this help message and exit
  -i PDBQTFILES         [REQUIRED] Path to the Docking ready PDBQT file folder                   
  -c CSV                [REQUIRED] Path to the CSV file containing summarised docking results
  -n NEWFOLDER          [REQUIRED] Path to the new folder                     
  -t TOP                [REQUIRED] Top selection
```

Enjoy virtual screening. For any issues that arise please contact the Bruning Lab directly.
