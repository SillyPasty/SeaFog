# include <stdio.h>
# include <string.h>
# include <stdlib.h>
# include <time.h>
# include <stddef.h>
# include "hisd.h"
# include "hisd2netcdf.h"
# include "date_utl.h"
# include <math.h>
# include "png.h"
# include "zlib.h"

# define  MAXFILE   10
# define  INVALID   -1

# define  WIDTH     5501	/* default pixel number */
# define  HEIGHT    2001	/* default line number */
# define  LTLON     119.0	/* default left top longitude */
# define  LTLAT     30.16	/* default left top latitude */
# define  DLON      0.005	/* default Spatial resolution (longitude) */
# define  DLAT      0.005	/* default Spatial resolution (latitude) */

# define  ERROR   -1
// # define  size   1080
# define PNGW 3600
# define PNGH 2160
# define OFFSET 200 //gray value - offset
typedef struct{
	char	*InFile[MAXFILE+1];
	char	*OutFile;
	char	filenum;
}argument;

typedef struct {
	float	*lon;
	float	*lat;
}geo_outdata;

typedef struct{
	//float	*lon;
	//float	*lat;
	float	*phys;	// ����ֵ
	double	startTime;
	double	endTime;
	char	satName[32];
}outdata;

typedef struct{
	short	width;		/* -width    pixel number */
	short	height;		/* -height   line number  */
	double	ltlon;		/* -lon      left top longitude */
	double	ltlat;		/* -lat      left top latitude  */
	double	dlon;		/* -dlon     Spatial resolution (longitude) */
	double	dlat;		/* -dlat     Spatial resolution (latitude) */
	short	band;
}parameter;


/* ------------------------------------------------------------------------- */
int getData(argument *arg, parameter *param, outdata *data);
/* ---------------------------------------------------------------------------
  getData()
 -----------------------------------------------------------------------------*/
int getData(argument *arg,parameter *param,outdata *data){

	HisdHeader		**header;
	FILE			**fp;
	geo_outdata     geo_data;
	float			*Pix,*Lin;
	unsigned short	*startLine;
	unsigned short	*endLine;
	unsigned int	ii,jj,kk,ll;
	int				k, n;
	unsigned short	count;
	float			radiance;
	unsigned long	n_size = param->height * param->width;
	double			phys = 0.0;
	float 			minLine = 99999.0;
	float			maxLine =-99999.0;
	int             flag = 0;
	float           maxValue = -9999.0;
	float           minValue =  9999.0;
	// updated in 4.1
	float           log_root;
	float           denom;

	log_root = log10(0.0223);
	denom = (1 - log_root) * 0.75;

	/* 0. allocate */
	if (NULL == (geo_data.lat = (float *)calloc(param->height, sizeof(float *))) ||
		NULL == (geo_data.lon = (float *)calloc(param->width, sizeof(float *)))) {
		fprintf(stderr, "callocate error\n");
		return(ERROR_CALLOCATE);
	}
	/* 0.5 ��ʼ�� */
	for (ii = 0; ii < param->height; ii++) {
		geo_data.lat[ii] = param->ltlat - param->dlat * ii;
	}
	for (ii = 0; ii < param->width; ii++) {
		geo_data.lon[ii] = param->ltlon + param->dlon * ii;
	}
	/* 0.6 ��¼���澭γ����Ϣ */
	// printf("%d", arg->filenum);
	/* 1 allocate */
	if(	NULL == ( header = (HisdHeader **)calloc(arg->filenum,sizeof(HisdHeader *))) ||
		NULL == ( fp = (FILE **)calloc(arg->filenum,sizeof(FILE *))) || 
		NULL == ( startLine = (unsigned short *)calloc(arg->filenum,sizeof(unsigned short *))) ||
		NULL == ( endLine   = (unsigned short *)calloc(arg->filenum,sizeof(unsigned short *))) ||
		NULL == ( Pix = (float *)calloc(n_size,sizeof(float *))) ||
		NULL == ( Lin = (float *)calloc(n_size,sizeof(float *)))
	){
		fprintf(stderr,"callocate error\n");
		return(ERROR_CALLOCATE);
	}
	n = -1;
	for(ii=0;ii<arg->filenum;ii++){
		/* 2-1 open file */
		if(NULL == ( fp[ii] = fopen(arg->InFile[ii], "rb"))){
			fprintf(stderr,"error... : can not open [%s]\n",arg->InFile[ii]);
			continue;
		}
		/* 2-2 callocate */
		if(NULL == (header[ii] = (HisdHeader *)calloc(1,sizeof(HisdHeader)))){
			fprintf(stderr,"callocate error\n");
			return(ERROR_CALLOCATE);
		}
		/* 2-3 read hisd header */
		
		if(NORMAL_END != hisd_read_header(header[ii],fp[ii])){
			fprintf(stderr,"error : read header [%s]\n",arg->InFile[ii]);
			continue;
		}
		/* 2-4 starLine and endLine */
		startLine[ii] = header[ii]->seg->strLineNo;
		endLine[ii]   = startLine[ii] + header[ii]->data->nLin -1;
		/* 2-5 check header consistency */
		if(n==-1)n=ii;
		if(	header[n]->calib->bandNo       != header[ii]->calib->bandNo ||
			header[n]->calib->gain_cnt2rad != header[ii]->calib->gain_cnt2rad ||
			header[n]->proj->loff          != header[ii]->proj->loff    ||
			header[n]->proj->coff          != header[ii]->proj->coff    ){
			fprintf(stderr,"header consistency error\n");
			fprintf(stderr,"%s : %s\n",arg->InFile[n],arg->InFile[ii]);
			return(ERROR_INFO);
		}
		n=ii;
	}
	/* 2-6 check file open */
	if(n==-1){
		//
		fprintf(stderr,"error : can not open all files\n");
		return(ERROR_FILE_OPEN);
	}
	/* 2-6 satellite name & band number */
	param->band = header[n]->calib->bandNo;
	strcpy(data->satName , header[n]->basic->satName);

	/* 3 get data */
	for(jj=0;jj<param->height;jj++){
	for(ii=0;ii<param->width;ii++){
		/* 3-1 init */
		count = header[n]->calib->outCount;
		kk = jj * param->width + ii;
		/* 3-2 convert lon & lat to pix & lin */
		lonlat_to_pixlin(header[n],geo_data.lon[ii], geo_data.lat[jj],&Pix[kk],&Lin[kk]);
		/* 3-3 min & max line */
		if(minLine > Lin[kk]) minLine =  Lin[kk];
		if(maxLine < Lin[kk]) maxLine =  Lin[kk];
		/* 3-4 get count value */
		for(ll=0;ll<arg->filenum;ll++){
            // 2015.06.06  fixed bug
	//		if(startLine[ll] <=  Lin[kk]+0.5 && Lin[kk]+0.5 <= endLine[ll]){
			if(startLine[ll] -0.5 <=  Lin[kk] && Lin[kk] < endLine[ll] + 0.5){
				hisd_getdata_by_pixlin(header[ll],fp[ll],Pix[kk],Lin[kk], &count);
				break;
			}
		}
		/* 3-5 check count value */
		if( count == header[n]->calib->outCount || 
			count == header[n]->calib->errorCount){
			data->phys[kk] = INVALID;
		}else{
		/* 3-6 convert count value to radiance */
			radiance = (float)count * header[n]->calib->gain_cnt2rad +
						header[n]->calib->cnst_cnt2rad;

		/* 3-6 convert radiance to physical value */
			if(	(header[n]->calib->bandNo>=7 &&
				 strstr(header[n]->basic->satName,"Himawari")!=NULL ) ||
				(header[n]->calib->bandNo>=2 &&
				 strstr(header[n]->basic->satName,"MTSAT-2") !=NULL )){ //MTSAT-2 is Himawari7
				/* infrared band */
				hisd_radiance_to_tbb(header[n],radiance,&phys);
				// 183.15 = 273.15 - 90
				//phys = (phys - 183.15) * 256 / 120;
				//phys = (phys - 220) / 35 * 256;
				data->phys[kk] = (float)phys;
				flag = 1;
			}else{
				/* visible or near infrared band */

				phys = header[n]->calib->rad2albedo * radiance * 255;
				//phys += 30;
				data->phys[kk] = phys;
				flag = 0;
			}
		}
	}
	}
	/* 3.9  Range ���� */

	/* 3.9.1 ���ά���� ���ֵ��Сֵ */
	for (int i = 0; i < param->height; ++i) {
		for (int j = 0; j < param->width; ++j) {
			//k = j * param->width + i;
			k = i * param->width + j;
			if (data->phys[k] > maxValue)
				maxValue = data->phys[k];
			if (data->phys[k] < minValue)
				minValue = data->phys[k];
		}
	}
	/* 3.9.2 Max Min check */
	if (9999.0 == minValue ||
		-9999.0 == maxValue) {
		printf("Error �������ֵʧ�ܣ�\n");
		exit(0);
	}
	if (0 == flag) {
		/* �ɼ���ͨ������ */
		minValue = minValue * 0.05;
		maxValue = maxValue * 0.85
			;
	}
	else if (1 == flag) {
		minValue = minValue;
		maxValue = maxValue;
	}
	/* 3.9.3 ���нض� */
	for (int i = 0; i < param->height; ++i) {
		for (int j = 0; j < param->width; ++j) {
			k = i * param->width + j;
			if (data->phys[k] > maxValue)
				data->phys[k] = maxValue;
			else if (data->phys[k] < minValue)
				data->phys[k] = minValue;
			if (1 == flag)
				// rewrite by zwf
				data->phys[k] = data->phys[k]-OFFSET;//(data->phys[k] - minValue) / (maxValue - minValue) * 255;
				if (data->phys[k] >255) data->phys[k] = 255;
				if (data->phys[k] <0) data->phys[k] = 0;

			else if (0 == flag) {
				// cira stretch
				data->phys[k] /= 255;
				data->phys[k] = (log10(data->phys[k]) - log_root) * 255 / denom;
				if (data->phys[k] > 255) {
					data->phys[k] = 255;
				}
				else if (data->phys[k] < 0) {
					data->phys[k] = 0;
				}

			}
		}
	}
	
	
	/* 4 convert maxLine & minLine to scanTime */
	for(ll=0;ll<arg->filenum;ll++){
		/* 4-1 startTime */
		if(startLine[ll] <= minLine && minLine <= endLine[ll]){
			for(ii=1;ii<header[ll]->obstime->obsNum;ii++){                                                                                       
				if(minLine < header[ll]->obstime->lineNo[ii]){
					data->startTime = header[ll]->obstime->obsMJD[ii-1];
					break;
				}else if(minLine == header[ll]->obstime->lineNo[ii]){
					data->startTime = header[ll]->obstime->obsMJD[ii];
					break;
				}
			}
		}
		/* 4-2 endTime */
		if(startLine[ll] <= maxLine && maxLine <= endLine[ll]){
			for(ii=1;ii<header[ll]->obstime->obsNum;ii++){
				if(maxLine < header[ll]->obstime->lineNo[ii]){
					data->endTime = header[ll]->obstime->obsMJD[ii-1];
				}else if(maxLine == header[ll]->obstime->lineNo[ii]){
					data->endTime = header[ll]->obstime->obsMJD[ii];
				}
			}
		}
	}

	/* 5 check data */
	/*
	for (int i = 0; i < param->height; i = i + param->height / 20) {
		printf("%6.1f ", Pix[i]);
	}
	printf("\n");
	for (int i = 0; i < param->height; i = i + param->height / 20) {
		printf("%6.1f ", Lin[i]);
	}
	printf("\n");
	printf("Satellite Name : %s\n",data->satName);
	printf("Band Number    : %d\n",param->band);
	printf("physical value :\n      ");
	for(jj=0;jj<param->width ;jj=jj+param->width/20){
		printf("%6.1f ", geo_data.lon[jj]);
	}
	printf("\n");
	for(ii=0;ii<param->height;ii=ii+param->height/20){
		kk = ii * param->width + jj;
		printf("%6.1f ",geo_data.lat[ii]);
		for(jj=0;jj<param->width ;jj=jj+param->width/20){
			kk = ii * param->width + jj;
			printf("%6.2f ",data->phys[kk]);
		}
		printf("\n");
	}
	*/

	/* 6 free */
	for(ii=0;ii<arg->filenum;ii++){
		if(header[ii] != NULL){
			hisd_free(header[ii]);
		}
		if(fp[ii]     != NULL){
			 fclose(fp[ii]);
		}
	}
	free(header);
	free(fp);
	free(startLine);
	free(endLine);
	free(Pix);
	free(Lin);
	free(geo_data.lat);
	free(geo_data.lon);
	return(NORMAL_END);
}


/* Write a png file */
int write_png(char *file_name,outdata *data)
{
   FILE *fp;
   png_structp png_ptr;
   png_infop info_ptr;
   png_colorp palette;
   const int height = PNGH;
   const int width = PNGW;
   const int bytes_per_pixel=1;

   /* Open the file */
   fp = fopen(file_name, "wb");
   if (fp == NULL)
      return (ERROR);

   /* Create and initialize the png_struct with the desired error handler
    * functions.  If you want to use the default stderr and longjump method,
    * you can supply NULL for the last three parameters.  We also check that
    * the library version is compatible with the one used at compile time,
    * in case we are using dynamically linked libraries.  REQUIRED.
    */
   //png_voidp user_error_ptr;
   //png_error_ptr user_error_fn, user_warning_fn;
   png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
   if (png_ptr == NULL)
   {
      fclose(fp);
      return (ERROR);
   }

   /* Allocate/initialize the image information data.  REQUIRED. */
   info_ptr = png_create_info_struct(png_ptr);
   if (info_ptr == NULL)
   {
      fclose(fp);
      png_destroy_write_struct(&png_ptr,  NULL);
      return (ERROR);
   }

   /* Set up error handling.  REQUIRED if you aren't supplying your own
    * error handling functions in the png_create_write_struct() call.
    */
   if (setjmp(png_jmpbuf(png_ptr)))
   {
      /* If we get here, we had a problem writing the file. */
      fclose(fp);
      png_destroy_write_struct(&png_ptr, &info_ptr);
      return (ERROR);
   }

   /* One of the following I/O initialization functions is REQUIRED. */

//#ifdef streams /* I/O initialization method 1 */
   /* Set up the output control if you are using standard C streams. */
   png_init_io(png_ptr, fp);

   /* This is the hard way. */

   /* Set the image information here.  Width and height are up to 2^31,
    * bit_depth is one of 1, 2, 4, 8 or 16, but valid values also depend on
    * the color_type selected.  color_type is one of PNG_COLOR_TYPE_GRAY,
    * PNG_COLOR_TYPE_GRAY_ALPHA, PNG_COLOR_TYPE_PALETTE, PNG_COLOR_TYPE_RGB,
    * or PNG_COLOR_TYPE_RGB_ALPHA.  interlace is either PNG_INTERLACE_NONE or
    * PNG_INTERLACE_ADAM7, and the compression_type and filter_type MUST
    * currently be PNG_COMPRESSION_TYPE_BASE and PNG_FILTER_TYPE_BASE.
    * REQUIRED.
    */
//   png_set_IHDR(png_ptr, info_ptr, width, height, bit_depth,
//       PNG_COLOR_TYPE_???, PNG_INTERLACE_????,
//       PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
   png_set_IHDR(png_ptr, info_ptr, width, height, 8,
       PNG_COLOR_TYPE_GRAY, PNG_INTERLACE_NONE,
       PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);

   /* Write the file header information.  REQUIRED. */
   png_write_info(png_ptr, info_ptr);

    /* Pack pixels into bytes. */
   png_set_packing(png_ptr);

   /* The easiest way to write the image (you may have a different memory
    * layout, however, so choose what fits your needs best).  You need to
    * use the first method if you aren't handling interlacing yourself.
    */
   png_uint_32 k;

   /* In this example, "image" is a one-dimensional array of bytes. */

   /* Guard against integer overflow. */
   if (height > PNG_SIZE_MAX / (width * bytes_per_pixel))
      png_error(png_ptr, "Image data buffer would be too large");

   //png_byte image[height * width * bytes_per_pixel];
   png_bytep row_pointers[height];
   png_byte* image;


   if (NULL == (image = (png_byte*)calloc(height * width * bytes_per_pixel, sizeof(png_byte*)))) {
	   fprintf(stderr, "callocate error\n");
	   return(ERROR_CALLOCATE);
   }

   /*
   if (NULL == (geo_data.lat = (float*)calloc(param->height, sizeof(float*))) ||
	   NULL == (geo_data.lon = (float*)calloc(param->width, sizeof(float*)))) {
	   fprintf(stderr, "callocate error\n");
	   return(ERROR_CALLOCATE);
   }*/

   for(int i=0;i<height*width;i++)
	   image[i]=(char)data->phys[i];


   if (height > PNG_UINT_32_MAX / (sizeof (png_bytep)))
      png_error(png_ptr, "Image is too tall to process in memory");

   /* Set up pointers into your "image" byte array. */
   for (k = 0; k < height; k++)
      row_pointers[k] = image + k * width * bytes_per_pixel;

   /* One of the following output methods is REQUIRED. */


   png_write_image(png_ptr, row_pointers);


   /* If you png_malloced a palette, free it here.
    * (Don't free info_ptr->palette, as shown in versions 1.0.5m and earlier of
    * this example; if libpng mallocs info_ptr->palette, libpng will free it).
    * If you allocated it with malloc() instead of png_malloc(), use free()
    * instead of png_free().
    */
   //png_free(png_ptr, palette);
   //palette = NULL;

 
   /* Whenever you use png_free(), it is a good idea to set the pointer to
    * NULL in case your application inadvertently tries to png_free() it
    * again.  When png_free() sees a NULL it returns without action, avoiding
    * the double-free problem.
    */

   /* Clean up after the write, and free any allocated memory. */
   png_destroy_write_struct(&png_ptr, &info_ptr);

   /* Close the file. */
   free(image);
   fclose(fp);

   /* That's it! */
   return (1);
}

int main(int argc, char* argv[]) {

	time_t t;    
	// time(&t);    
    // printf("initial: %s\n",ctime(&t));// ctime(&t)将日期转为字符内串并打印容
	/* 0. Variable */
	parameter	param;
	argument	arg;
	outdata		data;
	long		n_size;
	long		ii;
	
	/* 1. Init Parameter */
	//param.ltlat = 41.35;		// modify value here
	//param.ltlon = 115;
	param.ltlat = 45;//38.86;		// modify value here
	param.ltlon = 105;//117.5;		// ѡ���Ӧ�ľ�γ��
	//param.ltlon = 100.4;
	param.width = PNGW;//size; # w he h,xie fan le 
	param.height = PNGH;//size;		// image.shape
	param.dlat = 0.0125;//0.0055;		// �����ֱ���
	param.dlon = 0.0125; //0.0055;			

	// printf("Left top (lat,lon) : (%6.2f,%6.2f)\n", param.ltlat, param.ltlon);
	// printf("width,height       : (%6d,%6d)\n", param.width, param.height);
	// printf("Spatial resolution : (%6.3f,%6.3f)\n", param.dlat, param.dlon);
	n_size = param.width * param.height;

	/* 2. Allocate */
	if (NULL == (data.phys = (float*)calloc(n_size, sizeof(float*)))) {
		fprintf(stderr, "allocate error\n");
		return(ERROR_CALLOCATE);
	}
	// time(&t);    
    // printf("allocate: %s\n",ctime(&t));// ctime(&t)将日期转为字符内串并打印容
	/* init */
	for (ii = 0; ii < n_size; ii++) {
		data.phys[ii] = INVALID;
	}
	/* 3. ���ļ� */
	//update in 4.11

	//ԭ����
	/* 4. GetData && Make Png */

	for(int i=0; i<argc-2; i++){
		arg.InFile[i] = (char*) argv[i+2];
	}
	// time(&t);    
    // printf("getdata: %s\n",ctime(&t));// ctime(&t)将日期转为字符内串并打印容
	//arg.InFile[3] = "HS_H08_20170312_0000_B01_FLDK_R10_S0510.DAT";
	// arg.InFile[0] = (char*) "../data/HS_H08_20170312_0000_B01_FLDK_R10_S0210.DAT";
	// arg.InFile[1] = (char*) "../data/HS_H08_20170312_0000_B01_FLDK_R10_S0310.DAT";
	//arg.InFile[2] = (char*) "../data/HS_H08_20170312_0000_B01_FLDK_R10_S0410.DAT";
	// arg.InFile[3] = "HS_H08_20190510_0000_B01_FLDK_R10_S0510.DAT";

	arg.filenum = argc-2;

	/* 4.2 ����getData����*/
	if (NORMAL_END != getData(&arg, &param, &data)) {
		fprintf(stderr, "get data error\n");
		free(data.phys);
		return(ERROR_READ_DATA);
	}

	// time(&t);    
    // printf("freedata: %s\n",ctime(&t));// ctime(&t)将日期转为字符内串并打印容

	/* 4.3 Make Png */
	write_png((char*)argv[1], &data);

	// time(&t);    
    // printf("write_png: %s\n",ctime(&t));// ctime(&t)将日期转为字符内串并打印容
	// printf("Write Png Normal end..\n");
	/* 5. free */
	free(data.phys);

	// time(&t);    
    // printf("end: %s\n",ctime(&t));// ctime(&t)将日期转为字符内串并打印容
	/* 6. End */
	// printf("NORMAL END\n");
	//return(NORMAL_END);
	return 0;

}
