# Real-time detection tool of attacks leveraging Domain Administrator privilege

## How to implement the tool
###	Tool detail
* <a href="https://github.com/sisoc-tokyo/Real-timeDetectionAD/tree/master/detectionTools">Detection tools</a>
    * Files
        * rest_ocsvm_gt.py: REST API for detection. It is called by Logstash.
        * signature_detection.py: Signature-based detection program. It is called by rest_ocsvm_gt.py.
        * machine_learning.py: Machine learning detection program. It is called by rest_ocsvm_gt.py.
        * send_alert.py: Program for sending alert mail. It is called by rest_ocsvm_gt.py.
        * ocsvm_gt_XXXX.pkl files: Model files. They are created by Goldenticket_One-class_SVM.ipynb
        * data_dummies_XXXX.csv: One-Hot encoding dummy files. They are created by Goldenticket_One-class_SVM.ipynb
    * Location: Deploy on Detection Server
    * How to use: launch rest_ocsvm_gt.py 
    * Notes: REST API is running on Flask.

* <a href="https://github.com/sisoc-tokyo/Real-timeDetectionAD/tree/master/logstash">Configuration files for Logstash</a>
    * Files
        * logstash_winlogbeat.conf: Configuration file of Logstash. Logs are sent through the pipline of Logstash. Logstash extract data for detection from logs and call the REST API "rest_ocsvm_gt.py".<br/>
        This file should be located in Log Server where Logstash is running. 
    * Location: Deploy on Log Server
    * How to use: 
        * Launch Logstash by specifing the conf file.<br/>
	    e.g.）logstash -f /etc/logstash/conf.d/logstash_winlogbeat.conf &<br/>

* <a href="https://github.com/sisoc-tokyo/Real-timeDetectionAD/tree/master/winlogbeat">Configuration files for Winlogbeat</a>
    * Files
        * winlogbeat.yml: Configuration file of Winlogbeat. This file should be located in Domain Controller where Winlogbeat is running. 
    * Location: Place in the install directory of Winlogbeat on Domain Controller
    * How to use: 
	    * Star Winlogbeat on Domain Controller
 
* <a href="https://github.com/sisoc-tokyo/Real-timeDetectionAD/tree/master/learningTools">Learning tools</a>
    * Files
        * ADLogParserForML: Java programs to prepare for creating input for Goldenticket_One-class_SVM.ipynb. This programs extract data from Event Logs exported as CSV files.
        * Goldenticket_One-class_SVM.ipynb : A Python program runnung on the Jupyter Notebook to create model and calculate detection rate.
    * Location: Deploy on Detection Server
    * How to use: 
        1. Export Domain Controller Event logs as CSV file format using built-in Windows function (Rigiht click Event Logs and save as csv file).
        2. Execute ADLogParserForML using the above Event Logs as inputs. Then parsed csv file (eventlog.csv) will be created.<br/>
        <pre>
        # cd ADLogParserForML/bin
        # java logparse/AuthLogParser /Users/Documents/tmp/input /Users/marikof/Documents/tmp/output  /Users/Documents/tmp/input/command.txt /Users/marikof/Documents/tmp/input/adminlist.txt
        </pre>
        3. If you want to eveluate the detection rate, organize the value of "target" column as follows.
            * train
            * test
            * outlier
                        
            "train" data is training data and should be in normal states. Machine learning learns these data.
            "test" data means normal data. Machine lerning doe's not learn these data, they are used only for evaluation. Please change some target value from "train" to "test".
            "outlier" data means outlier data. Machine lerning doe's not learn these data, they are used only for evaluation. Please change some target value from "train" to "outlier" and change its account value and process value to other. You can also conducte unusual behavior to create outlier logs.
          
        4. Execute One-class_SVM.ipynb. You should specify the file path of eventlog.csv. <br/>
            You will get model files (ocsvm_gt_XXXX.pkl) and One-Hot encoding dummy files (data_dummies_XXXX.csv).
            
        5. If you want to see detection result, please check X_outliers_resultXXXX.csv, X_test_resultXXXX.csv and X_ourlier_resultXXXX.csv files.The rightmost column shows result, "1" means normal and "-1" means outlier.


  
