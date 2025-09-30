HPC Zone
Data Storage Zone
Access Zone
Management Zone

- Storage should only be mounted by HPC Node
- Performance degradataion when a certain treshold is reached, should be regularly pruned of unwanted files. (delete old files, move job output to campaign storage)
- Campaign storage use less expensive storage to archived related project output (stored for years)
- Archive storage to retain for decades
- Campaign + Archive can use NVME or SSD as cache backed by spinning disk or tape
- Burst buffer collacated within HPC compute node ( can be local, can be remote-shared between mutliple nodes)

Access Zone:
- login nodes to submit job and visualization
- transfer node to transfer data in and out of HPC, can also provide storage mounting service (usually use Science DMZ)
- web portal nodes for web interfaces to HPC services

Management Zone:
- separate security posture ( access via bastion or VPN)
- store config data, node images, logs
- DNS, DHCP, Authentication and Authorization, NTP, log management, version controlled repo
- Config management server (xcat ?)
- Slurm ( access by non priv user through API and specific commands )

- MFA for Access Zone
- File system encryption 

- Granular data access



