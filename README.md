# CSCI-3130-Grader
Small program that saves huge amount of time on grading logisim labs.

You may find student list (students_list2.txt) or create your own and import it. Please note that there is no gui interface for student list import, but you can just call load_student_list_into_grades_db() function and provide correct name of the expected file.

Installation and grading:

apt-get install python3 numpy python3-pip wkhtmltopdf
pip3 install --user numpy pyqt5 pandas pathlib pdfkit wkhtmltopdf 


How to run in Ubuntu (basic how to for people without experience in Linux). 
1. Install Ubuntu. Install updates.
2. type "sudo apt-get install python3 python3-pip git" and enter admin passwords that you created during the previous step.
3. type "pip3 install --user numpy pyqt5 pandas pathlibls
4. go to the directory where you want to put grader program (cd ...) and type "git clone https://github.com/fio2003/CSCI-3130-Grader.git"
5. type ./main.py and you should see main program window.
6. press 'Settings' button. In new window fill desired path for grades DB. For example, ./grades.sqlite3. You may type any name you like.
7. press 'OK' or 'Apply'. You should see a pop-up window that will ask you to confirm settings DB creation. Then another window for grades DB.
In terminal you should see that all tables were created and filled with the default data.
8. Open 'Settings' again and fill paths to logisim, local storage and remote storage in 'User paths' area. 
For example, Logisim path: ~/Downloads/logisim.jar
Local lab storage: ./local_dir/
Remote lab storage: ./remote_dir/. Please note, that it does not have to be local folder, but remote server ip with your username (there is no password field so you have to install ceritificates before the connection).
9. Select grading year and semester. Type your name in "Grader name" and what sync command you want to use. For example, 'rsync -avz'.
10. Close Settings.
11. 'Manage labs' should now become active - click on it.
12. Click on 'Sync to local storage' - it will syncronize local repository with local one.
13. Select lab to work with.
14. Click on 'Create due dates' and select 'Submission date'. Other resubmissions are going to be set automatically, but you can override them.
15. Click on 'Import labs'. It will check current date and import labs to local lab storage. Note, only latest submission is going to be imported. If for some reasons you did not grade 
16. Close 'Manage labs'
17. Doubleclick on top input line and select lab to start grading or singleclick and type correct path.
18. Click on 'Open'. 
19. Click on 'Begin'
20. Grade labs... Do not forget to click on 'save all' or just select 'autosave'.
21. Click on 'Generate reports'. It will create 'Answers' directory in local lab folder.
22. Open 'Manage labs'.
23. Select lab to work with.
24. Click on 'Export pdfs'. It will sync pdfs created during step 21.


Screenshots:
![gui](https://github.com/fio2003/CSCI-3130-Grader/blob/master/screenshot1.png "gui")
![report](https://github.com/fio2003/CSCI-3130-Grader/blob/master/screenshot2.png "report")