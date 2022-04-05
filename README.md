# IIOT CNC Monitoring Python Source Code.


### About the Project 
This project is a Customized Solution developed especially for a Crankshaft Manufacturing Company(Netalkar Industries Belgaum) to help them track thier entire line inspection of Crankshaft Manufacturing, to help them track their Operator, Production Output and Machine Efficiency as well as to achive their dream of making their factory **paperless**.

#### Features of this Solution
1. This Device collects all the signals generated by CNC Machine which can help the authorities to track if any issues are happening with the machine in advance.
2. This Device helps in tracking Operator Efficiency. 
3. This device records energy consumption done by the machine which helps authorities to track health of machine.
4. Incase any alarm is generated on the machine, Operator is asked to enter the reasons for the alarm as it will help the authorities to track if any issues happening with the machine.
5. If Machine is found Idle for a long duration of time then device will not allow the operator to start the machine until he enters the reason why the machine was idle for long time.
6. It tracks the production done by every operator in every shift on every machine.(Before this the proces was done using pen and paper)
7. Sometimes it is found that a NC Job(Damaged Job) is loaded on machine which results in unnecessary consumption of energy as well as results in wastage of time . The Device Tracks if any Damaged Job is loaded on the machine and alerts the operator that he cannot start the machine as the JOB is already damaged.
8. It Tracks the overall idle time of the machine.
9. This device continously uploads the data collected to the in house SERVER, also if it is not able to make connection with the SERVER, then it stores all the data in local Database to avoid Data Loss.

## Screenshots
1. **IIOT CNC Monitoring Device.** 
 ![Not found](./screenshots/ss8)
2. **Device Installed on CNC Machine.** 
 ![Not found](./screenshots/ss14) 

3. **Admin Dashbaord or Configuration of Device** 
 ![Not found](./screenshots/ss7) 

4. **Operator Dashboard to enter JOB Id's** 
 ![Not found](./screenshots/ss10) 

5. **Alarm Screen** 
 ![Not found](./screenshots/ss11) 

6. **Machine Idle for long Time Screen** 
 ![Not found](./screenshots/ss9) 
 


#### These are only the python files of the project and this repository doesnot include files of React Application

### To know what every file does as well as dependencies please look into the README_FILES Folder 

### This Project will not run on computer but needs special microprocessors like raspberry PI. Feel Free to Contact me if you want to know more.