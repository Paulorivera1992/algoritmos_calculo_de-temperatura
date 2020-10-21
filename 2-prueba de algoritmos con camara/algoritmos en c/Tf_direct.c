#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>       /* round() */
#include <time.h> 
#include "tiffio.h"

double max(double a, double b, double c);
double countingSort (double *numbers, int size, double *B, double *C,int perc);
double TF(char *filename);
double calculo_temperatura_direct(double *R,double *G, double *B,int num_pixel);
void leer_matriz_T(double *T);
double calculo_temperatura_rec_spectral(double *R,double *G,double *B,int num_pixel);

int main(int argc, char* argv[])
{
  //FILE* tiempo;
  
  FILE* valor;
  valor = fopen("Tf_direct_temp.txt", "at");
  char tempe[100];
  double temperatura=TF(argv[1]);
  printf("la temperatura es: %6.10f \n", temperatura);
  
  gcvt(temperatura, 15, tempe); 
  strcat(tempe, "\n");
  fputs(tempe, valor);
  
  fclose(valor); 
}



//////////////////////calculo de V////////////////////////////7
double max(double a, double b, double c) {
   return ((a > b)? (a > c ? a : c) : (b > c ? b : c));
}

////////////////////calculo de percentiles///////////////////////////
double countingSortMain (double *numbers, double k, int size, double *B, double *C,int perc) {
    int i, j, indexB = 0;
    B = (double*) malloc(sizeof(double) * (size + 1));
    C = (double*) calloc((k + 1), sizeof(double));
    for (i = 0; i < size; i++) {
        C[(int)numbers[i]] = C[(int)numbers[i]] + 1;
    }
    for (i=0; i <= k; ++i) {
        for(j=0; j < C[i]; ++j) {
            B[indexB] = i;
            indexB++;
        }
    }
    int x= perc*(size)/100;
    double percentil=(B[x-1]);
    free(B);
    free(C);
    return percentil;
}

double countingSort (double *numbers, int size, double *B, double *C,int perc) {
    int i; 
    double k=-1.0;
    for (i = 0; i < size; i++) {
        if (numbers[i] > k) {
            k = numbers[i];
        }
    }
    return countingSortMain(numbers, k, size, B, C, perc);
}


//////////////////////calculo de temperatura /////////////////////////////////
double TF(char *filename){
  int ancho, alto;
	int numero_pixeles;
  double* matriz_R;
  double* matriz_G;
  double* matriz_B;
  double* value;
  
  ////////////////////cargar imagen .tiff en matriz de colores RGB//////////////////////////////////
  TIFF* tiff; 
  TIFF * tif = TIFFOpen (filename, "r");
  if (tif) {
	  uint32 * raster;
	  TIFFGetField (tif, TIFFTAG_IMAGEWIDTH, &ancho);
	  TIFFGetField (tif, TIFFTAG_IMAGELENGTH, &alto);
	  numero_pixeles = ancho * alto;      
    matriz_R=malloc(numero_pixeles*sizeof(double));
    matriz_G=malloc(numero_pixeles*sizeof(double));
    matriz_B=malloc(numero_pixeles*sizeof(double));
    value=malloc(numero_pixeles*sizeof(double));
    
	  raster = (uint32*) _TIFFmalloc(numero_pixeles* sizeof (uint32));
	  if (raster != NULL) {
	    if (TIFFReadRGBAImage (tif, ancho, alto, raster, 0)) {
         for(int i=0; i<numero_pixeles; i++){
           matriz_B[i] = (double)TIFFGetB(raster[i]);
           matriz_G[i] = (double)TIFFGetG(raster[i]);
           matriz_R[i] = (double)TIFFGetR(raster[i]);
           value[i] = max(matriz_R[i], matriz_G[i], matriz_B[i]);
         }
	    }
	    _TIFFfree (raster);
	  }
	TIFFClose (tif);
  }
  
    
  /////////////////calculo de percentiles/////////
  double delta_min;
  double delta_max;
  double* b1=malloc(numero_pixeles*sizeof(double));
  double* c1=malloc(numero_pixeles*sizeof(double));
  delta_min=countingSort(value,numero_pixeles, b1, c1,96);
  delta_max=countingSort(value,numero_pixeles, b1, c1,100);
  
  ////aplicación de mascara////////////////////////
  int n=0;
  for(int i=0;i<numero_pixeles;i++){
    if(value[i]<delta_max && value[i]>delta_min){
      matriz_B[i]=matriz_B[i]/255;
      matriz_G[i]=matriz_G[i]/255;
      matriz_R[i]=matriz_R[i]/255;
      n=n+1;
      }
    else{
      matriz_B[i]=0;
      matriz_G[i]=0;
      matriz_R[i]=0;
    }    
  }
  
 
  //////////calculo temperatura//////////////////////7
  double temp;
  temp=calculo_temperatura_direct(matriz_R,matriz_G, matriz_B,numero_pixeles);
  //temp=calculo_temperatura_rec_spectral(matriz_R,matriz_G, matriz_B,numero_pixeles);

  free(b1);
  free(c1);
  free(value);
  free(matriz_R);
  free(matriz_G);
  free(matriz_B);
  return temp;
}

/////////////////calculo de temperatura direct///////////////////////////////////
double calculo_temperatura_direct(double *R,double *G,double *B,int num_pixel){
  double c2=1.4385*pow(10,-2);
  double lambda_B=473.5*pow(10,-9);
  double lambda_G=540*pow(10,-9);
  double lambda_R=615*pow(10,-9); 
  double maxTf=3000;         // limite superior de Temperatura
  double minTf=1000;         // limite inferior de Temperatura 
  int numero_no_zero=0;
  double suma=0;
  double rho[3];
  for(int i=0;i<num_pixel;i++) {
    rho[0]=(double)R[i];
    rho[1]=(double)0.7677*G[i];
    rho[2]=(double)0.3197*B[i];
    if(rho[0] >= 0.03 && rho[0] < 0.99 && rho[1] >= 0.01 && rho[1] < 0.99){
      double SS=0.3653*(pow((rho[0]/(rho[1]/0.7677)),2))-1.669*(rho[0]/(rho[1]/0.7677)) + 3.392;   // factor de forma obtenido experimental
      double num=c2*(1/(lambda_G)-1/(lambda_R));               //numerador de la ecuacion
      double denom=log(rho[0]/(rho[1]/0.7677)) + 6*log(lambda_R/lambda_G) + log(SS); //denominador de la ecuacion
      double temp=num/denom; //temperatura calculada
      //test sobrepaso limites
      if(isnan(temp)){//si es un nand
        suma=suma;      
      }
      else if (temp>maxTf) {// nivel superior
        suma=suma + maxTf;
        }
      else if(temp<minTf){ //nivel inferior
        suma=suma + minTf;
        }
      else {//minTf < Tf < maxTf valor correcto
        suma=suma + temp;
        }
      numero_no_zero=numero_no_zero+1;
     } 
    else{
       suma=suma;
       }
    }
  return suma/numero_no_zero;
}

/////////////////calculo de temperatura recuperacion espectral///////////////////////////////////
double calculo_temperatura_rec_spectral(double *R,double *G,double *B,int num_pixel){ 
  double c2=1.4385*pow(10,-2);
  double pl1=580*pow(10,-9);
  double pl2=620*pow(10,-9);
  double T[6];
  leer_matriz_T(T);
  double pE1;
  double pE2;
  double num;
  double denom;
  double temp;
  int maxTf=3000;         // limite superior de Temperatura
  int minTf=1000;         // limite inferior de Temperatura 
  int numero_no_zero=0;
  double rho[3];
  double suma=0;
  for(int i=0;i<num_pixel;i++) {
    rho[0]=(double)R[i];
    rho[1]=(double)0.7677*G[i];
    rho[2]=(double)0.3197*B[i];
    if(rho[0] >= 0.03 && rho[0] < 0.99 && rho[1] >= 0.01 && rho[1] < 0.99){
      numero_no_zero=numero_no_zero+1;  
      pE1 = T[0]*rho[0]+ T[1]*rho[1]+ T[2]*rho[2]; //faltan los valores de T
      pE2 = T[3]*rho[0]+ T[4]*rho[1]+ T[5]*rho[2]; //faltan los valores de T
      num=(c2*(pl1-pl2)/(pl1*pl2));//numerador de la ecuacion
      denom=(log((pE1*pow(pl1,5))/(pE2*pow(pl2,5))));//denominador de la ecuacion
      temp=num/denom; //temperatura calculada
      //test sobrepaso limites
      if(isnan(temp)){//si es un nand
        suma=suma;      
      }
      else if (temp>maxTf) {// nivel superior
        suma=suma + maxTf;
      }
      else if(temp<minTf){ //nivel inferior
        suma=suma + minTf;
      }    
      else {//minTf < Tf < maxTf valor correcto
        suma=suma + temp;
      }  
      } 
    else{
       suma=suma;
       }
    }
  return suma/numero_no_zero;
}

//////////carga elementos de la matriz T/////////////////////////////
void leer_matriz_T(double *T){ 
  FILE* fichero;
  fichero = fopen("T.txt", "r");
  fscanf(fichero, "%lf", &T[0]);
  fscanf(fichero, "%lf", &T[1]);
  fscanf(fichero, "%lf", &T[2]);
  fscanf(fichero, "%lf", &T[3]);
  fscanf(fichero, "%lf", &T[4]);
  fscanf(fichero, "%lf", &T[5]);
  fclose(fichero);
}