
int var=0;
int tableau[5];
int longueur ;

int etape=0;
void setup() {
  Serial.begin(9600);

  

}

void loop() {
  // put your main code here, to run repeatedly:

var=6;
 
 if (Serial.available())
  {
   if(Serial.read())
   {  
    
    longueur=sizeof(tableau)/4;  //il y a 4 octets pour un int 
    Serial.println(longueur); 
    
    for (int i=0; i<longueur;i++)
      {
      var++;
       tableau[i]=var;
      }

   

  
   for( int i=0; i<longueur;i++)
      {
      Serial.println(tableau[i]);
      delay(500);
      }
   }  
  }

}
