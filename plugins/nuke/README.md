#Nuke Submission Plugin

You'll need to add whatever directory you put the two files in to your PYTHONPATH and NUKE_PATH environment variables

It'll put a menu option on the bottom of the Render menu that allows you to submit

Also, if you use Ocula, you'll need to create a resource in the SGE complex configuration as follows:

    lic_ocula_r ocula_r INT  <= YES JOB 0 0

and add it to the global exec hosts list of consumable resources.  For more info on how this works, look here:
http://wikis.sun.com/display/gridengine62u2/Example+1+-+Floating+Software+License+Management
and:
http://wikis.sun.com/display/gridengine62u2/Defining+Consumable+Resources#DefiningConsumableResources-DefiningConsumableResources