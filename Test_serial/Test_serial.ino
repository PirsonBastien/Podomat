#define ROW_COUNT(array)    (sizeof(array) / sizeof(*array))
#define COLUMN_COUNT(array) (sizeof(array) / (sizeof(**array) * ROW_COUNT(array)))

int var=0;
int tableau[2][5]={{6,5,4,3,2},{7,6,5,4,3}};
int colonne ;
int ligne;
int etape=0;
int bascule=0;
void setup() {
  Serial.begin(9600);

  

}

void loop() {

 
 if (Serial.available())
  {
   if(Serial.read())
  {
    bascule=1;
  }
   if(bascule=1)
   {  
    bascule=0;
    ligne=ROW_COUNT(tableau);
    colonne=COLUMN_COUNT(tableau);
    Serial.println(ligne); 
    Serial.println(colonne);
   

  
   for( int i=0; i<ROW_COUNT(tableau);i++)
   {
      for( int j=0; j<COLUMN_COUNT(tableau);j++)

      {
      Serial.println(tableau[i][j]);
      }
      
   }
   }  
  }

}
