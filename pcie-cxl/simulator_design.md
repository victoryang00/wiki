

When I was designing the simulator I compared serveral back up solutions. I will tell why they are not working. So the problem is how to give ld/st interface desired delay from the application perspective.

## Hardware implementation
The original implementation of CXL.mem is they have a window inside the LLC, and if you access that 
![image-20231026123952716](image-20231026123952716.png)

## TMC Solution from Hiner and Yuanjiang

## Physical unplug Solution

lsmem to turn off

## PEMP dynamic region based Solution

## DAMON Solution from Amazon's 

## QEMU Solution

### Reference
1. https://airbus-seclab.github.io/qemu_blog/tcg_p3.html
2. https://lists.gnu.org/archive/html/qemu-devel/2017-01/msg03522.html
3. https://www.qemu.org/docs/master/devel/memory.html

## CXLMemSim Solution
