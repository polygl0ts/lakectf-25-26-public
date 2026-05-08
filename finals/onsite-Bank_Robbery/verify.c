#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/md5.h>



char hashedPassword[100] = "15dcdac23ec733cbf8267965e681a488";
char trueUID[16] = "AABBCCDDEE";
char adminPassword[100] = "ThisIsUseless";

void readline ( char * buf ) {
	 int c;
    int i = 0;

    // Read until newline or EOF
    while ((c = getchar()) != '\n') {
        buf[i++] = (char)c;
        if(i > 16){
	   puts("Hacking detected !! Exiting..." );
	   exit(0);
	}
    }
    buf[i] = '\0';  // Null-terminate
}

int get_number () {
 char buffer[100];
 readline(buffer); 
 return atoi(buffer);
}
void menu(){
    puts("Hello regular employee, What action do you whish to perform?");
    puts("1) Verify bank vault password");
    puts("2) upgrade session to admin");
    puts("3) exit");

}
void adminMenu(){
    puts("Welcome administrator, what do you want to do dear sir?");
    puts("1) Manage stored passwords");
    puts("2) Execute shellcode");
    puts("3) Log out of Admin");
}

void print_md5_sum(unsigned char* md) {
    int i;
    for(i=0; i < MD5_DIGEST_LENGTH; i++) {
        printf("%02x", md[i]);
    }
    printf("\n");
}
int main(){

    char UID[16];
    int isAdmin = 0;
    puts("Enter ID of employee card to access secure remote password authentication: ");
    gets(UID);
    puts("comparing strings...");
    if(strcmp(UID, trueUID) != 0){
        puts("wrong card ID, exiting");
        exit(0);
    }
    puts("Correct!");
    while(1){
    	if(isAdmin){
       	    adminMenu();
    	    switch(get_number()){
    	        case 1:{
    	            puts("Currently saved password: ");
    	            puts(hashedPassword);
    	            puts("Enter new password:"); 	           
    	            char temp[100];
    	            readline(temp);
    	            puts("Hashing for saving ...");
    	            puts("Error saving password: keeping previous one");
    	            break;
    	        }
    	        case 2:{
    	            puts("Enter shellcode to execute:");
    	            char shellcode[100];
    	            readline(shellcode);
    	            puts("Shellcode did not pass security inspection, attemped malicious activity. Exiting");
    	            exit(0);
    	        }
    	        case 3:{
    	            isAdmin = 0;
    	            break;
    	        }
    	        default: { break; }  
    	    } 	
    	}
    	else{
    	    menu();
    	    switch(get_number()){
    	        case 1:{
    	            puts("Enter bank vault password to verify:");
    	            char Pass[100];
 		    readline(Pass);
		    unsigned char result[MD5_DIGEST_LENGTH];
		    MD5((unsigned char*)Pass, strlen(Pass), result);
		    char md5string[60];
	            for(int i = 0; i < MD5_DIGEST_LENGTH; i++) {
			sprintf(&md5string[i * 2], "%02x", result[i]);
		    }
 		    if(strcmp(hashedPassword, md5string) == 0){
 		    	puts("Correct Password!. Login token = 4df8e71ac");
 		    }
 		    else{
                        puts("Incorrect vault password");
		    }
		    break;      
    	        }
    	        case 2:{
    	            puts("Enter Administrator Password: ");
    	            char adPass[100];
 		    readline(adPass);
 		    puts("Verifying password and attempting to log in...");
 		    if(strcmp(adPass, adminPassword) == 0){
 		    	puts("Congratulations, I dont know how you got here");
 		    	isAdmin = 1;
 		    }
 		    else{
                        puts("Error: isAdmin == 0 could not upgrade session to admin.");
		    }      
    	            break;
    	        }
    	        case 3:{
    	            exit(0);
    	        }
    	        default: { break; }  
    	    }
    	}
    	
    }
    return 0;
}
