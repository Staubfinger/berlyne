# Berlyne
Berlyne is a trainings platform for applied IT security.
 
The basic workflow is this:

* **Create a course**, activate scoreboard and write ups if wanted 
* **Assign software problems** to the course, in the form of CTF tasks
* Berlyne starts the required problems in virtual machines
* The problems description in the course gets updated with correct IP, ports and downloads
* **Participants join** the course and solve the problems
* Teacher accesses the course **write ups**

All that is done via a Web UI.

## Installing
On how to use Berlyne, please consult the wiki page [Installing Berlyne](https://github.com/rugo/berlyne/wiki/Installing-Berlyne)

## Problems
Tasks in Berlyne are called problems, for pun reasons.

It is very easy to create your own problems, see the [wiki](https://github.com/rugo/berlyne/wiki/Creating-Problems) 
for details.

Also have a look at the example problems:

* [Example Web Problem](https://github.com/rugo/berlyne/wiki/Example-Web-Problem)
* [Example Problem delivered with xinetd](https://github.com/rugo/berlyne/wiki/Example-xinetd-Problem)

## Finding Problems
Tasks can be shared via repository/download/usb stick whatever, since they only consist of
[three files](https://github.com/rugo/berlyne/wiki/Creating-Problems).

Tasks shared by membes of the community are stored in the
[Berlyne Tasks DB](http://tasks.wass-ctf.xyz). 

On how to install them, please consult the [wiki](https://github.com/rugo/berlyne/wiki/Installing-Problems).

## Virtual Machines
Berlyne automatically creates and starts VMs in the background and maps required ports to
the host system.

Supported providers for launching those VMs are:

* Docker **for developement**, see [wiki](https://github.com/rugo/berlyne/wiki/Security-Considerations)
* VirtualBox
* DigitalOcean, which is a cloud provider (API-Key needed)

## Contributing
Pull-Requests are very welcome.

If you want to share a task, please make sure to add the url to it to our
[Berlyne Tasks](http://tasks.wass-ctf.xyz) (don't forget to add your license)!
