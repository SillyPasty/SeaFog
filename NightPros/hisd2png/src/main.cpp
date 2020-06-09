#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fstream>
#include <time.h>
#include <stddef.h>
#include "hisd.h"
#include "hisd2netcdf.h"
#include "date_utl.h"
#include <math.h>

#define MAXFILE 10
#define INVALID -1

#define WIDTH 5501	/* default pixel number */
#define HEIGHT 2001 /* default line number */
#define LTLON 119.0 /* default left top longitude */
#define LTLAT 30.16 /* default left top latitude */
#define DLON 0.005	/* default Spatial resolution (longitude) */
#define DLAT 0.005	/* default Spatial resolution (latitude) */

# define PNGW 3600
# define PNGH 2160

#define ERROR -1
#define size 2048

typedef struct
{
	char *InFile[MAXFILE + 1];
	char *OutFile;
	char filenum;
} argument;

typedef struct
{
	float *lon;
	float *lat;
} geo_outdata;

typedef struct
{
	//float	*lon;
	//float	*lat;
	float *phys; // ����ֵ
	double startTime;
	double endTime;
	char satName[32];
} outdata;

typedef struct
{
	short width;  /* -width    pixel number */
	short height; /* -height   line number  */
	double ltlon; /* -lon      left top longitude */
	double ltlat; /* -lat      left top latitude  */
	double dlon;  /* -dlon     Spatial resolution (longitude) */
	double dlat;  /* -dlat     Spatial resolution (latitude) */
	short band;
} parameter;

/* ------------------------------------------------------------------------- */
int getData(argument *arg, parameter *param, outdata *data);
/* ---------------------------------------------------------------------------
  getData()
 -----------------------------------------------------------------------------*/
int getData(argument *arg, parameter *param, outdata *data)
{

	HisdHeader **header;
	FILE **fp;
	geo_outdata geo_data;
	float *Pix, *Lin;
	unsigned short *startLine;
	unsigned short *endLine;
	unsigned int ii, jj, kk, ll;
	int k, n;
	unsigned short count;
	float radiance;
	unsigned long n_size = param->height * param->width;
	double phys = 0.0;
	float minLine = 99999.0;
	float maxLine = -99999.0;
	int flag = 0;
	float maxValue = -9999.0;
	float minValue = 9999.0;
	// updated in 4.1
	float log_root;
	float denom;

	log_root = log10(0.0223);
	denom = (1 - log_root) * 0.75;

	/* 0. allocate */
	if (NULL == (geo_data.lat = (float *)calloc(param->height, sizeof(float *))) ||
		NULL == (geo_data.lon = (float *)calloc(param->width, sizeof(float *))))
	{
		fprintf(stderr, "callocate error\n");
		return (ERROR_CALLOCATE);
	}
	/* 0.5 ��ʼ�� */
	for (ii = 0; ii < param->height; ii++)
	{
		geo_data.lat[ii] = param->ltlat - param->dlat * ii;
	}
	for (ii = 0; ii < param->width; ii++)
	{
		geo_data.lon[ii] = param->ltlon + param->dlon * ii;
	}
	/* 0.6 ��¼���澭γ����Ϣ */

	/* 1 allocate */
	if (NULL == (header = (HisdHeader **)calloc(arg->filenum, sizeof(HisdHeader *))) ||
		NULL == (fp = (FILE **)calloc(arg->filenum, sizeof(FILE *))) ||
		NULL == (startLine = (unsigned short *)calloc(arg->filenum, sizeof(unsigned short *))) ||
		NULL == (endLine = (unsigned short *)calloc(arg->filenum, sizeof(unsigned short *))) ||
		NULL == (Pix = (float *)calloc(n_size, sizeof(float *))) ||
		NULL == (Lin = (float *)calloc(n_size, sizeof(float *))))
	{
		fprintf(stderr, "callocate error\n");
		return (ERROR_CALLOCATE);
	}
	n = -1;
	for (ii = 0; ii < arg->filenum; ii++)
	{
		/* 2-1 open file */
		if (NULL == (fp[ii] = fopen(arg->InFile[ii], "rb")))
		{
			fprintf(stderr, "error... : can not open [%s]\n", arg->InFile[ii]);
			continue;
		}
		/* 2-2 callocate */
		if (NULL == (header[ii] = (HisdHeader *)calloc(1, sizeof(HisdHeader))))
		{
			fprintf(stderr, "callocate error\n");
			return (ERROR_CALLOCATE);
		}
		/* 2-3 read hisd header */
		if (NORMAL_END != hisd_read_header(header[ii], fp[ii]))
		{
			fprintf(stderr, "error : read header [%s]\n", arg->InFile[ii]);
			continue;
		}
		/* 2-4 starLine and endLine */
		startLine[ii] = header[ii]->seg->strLineNo;
		endLine[ii] = startLine[ii] + header[ii]->data->nLin - 1;
		/* 2-5 check header consistency */
		if (n == -1)
			n = ii;
		if (header[n]->calib->bandNo != header[ii]->calib->bandNo ||
			header[n]->calib->gain_cnt2rad != header[ii]->calib->gain_cnt2rad ||
			header[n]->proj->loff != header[ii]->proj->loff ||
			header[n]->proj->coff != header[ii]->proj->coff)
		{
			fprintf(stderr, "header consistency error\n");
			fprintf(stderr, "%s : %s\n", arg->InFile[n], arg->InFile[ii]);
			return (ERROR_INFO);
		}
		n = ii;
	}
	/* 2-6 check file open */
	if (n == -1)
	{
		//
		fprintf(stderr, "error : can not open all files\n");
		return (ERROR_FILE_OPEN);
	}
	/* 2-6 satellite name & band number */
	param->band = header[n]->calib->bandNo;
	strcpy(data->satName, header[n]->basic->satName);

	/* 3 get data */
	for (jj = 0; jj < param->height; jj++)
	{
		for (ii = 0; ii < param->width; ii++)
		{
			/* 3-1 init */
			count = header[n]->calib->outCount;
			kk = jj * param->width + ii;
			/* 3-2 convert lon & lat to pix & lin */
			lonlat_to_pixlin(header[n], geo_data.lon[ii], geo_data.lat[jj], &Pix[kk], &Lin[kk]);
			/* 3-3 min & max line */
			if (minLine > Lin[kk])
				minLine = Lin[kk];
			if (maxLine < Lin[kk])
				maxLine = Lin[kk];
			/* 3-4 get count value */
			for (ll = 0; ll < arg->filenum; ll++)
			{
				// 2015.06.06  fixed bug
				//		if(startLine[ll] <=  Lin[kk]+0.5 && Lin[kk]+0.5 <= endLine[ll]){
				if (startLine[ll] - 0.5 <= Lin[kk] && Lin[kk] < endLine[ll] + 0.5)
				{
					hisd_getdata_by_pixlin(header[ll], fp[ll], Pix[kk], Lin[kk], &count);
					break;
				}
			}
			/* 3-5 check count value */
			if (count == header[n]->calib->outCount ||
				count == header[n]->calib->errorCount)
			{
				data->phys[kk] = INVALID;
			}
			else
			{
				/* 3-6 convert count value to radiance */
				radiance = (float)count * header[n]->calib->gain_cnt2rad +
						   header[n]->calib->cnst_cnt2rad;

				/* 3-6 convert radiance to physical value */
				if ((header[n]->calib->bandNo >= 7 &&
					 strstr(header[n]->basic->satName, "Himawari") != NULL) ||
					(header[n]->calib->bandNo >= 2 &&
					 strstr(header[n]->basic->satName, "MTSAT-2") != NULL))
				{
					/* infrared band */
					hisd_radiance_to_tbb(header[n], radiance, &phys);
					data->phys[kk] = (float)phys;
					flag = 1;
				}
				else
				{
					/* visible or near infrared band */

					phys = header[n]->calib->rad2albedo * radiance * 255;
					//phys += 30;
					data->phys[kk] = phys;
					flag = 0;
				}
			}
		}
	}
	if (flag == 0)
		return (NORMAL_END);
	/* 3.9  Range ���� */

	/* 3.9.1 ����?���� ���ֵ��С�? */
	for (int i = 0; i < param->height; ++i)
	{
		for (int j = 0; j < param->width; ++j)
		{
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
		-9999.0 == maxValue)
	{
		printf("Error �������ֵʧ�ܣ�\n");
		exit(0);
	}

	/* 4 convert maxLine & minLine to scanTime */
	for (ll = 0; ll < arg->filenum; ll++)
	{
		/* 4-1 startTime */
		if (startLine[ll] <= minLine && minLine <= endLine[ll])
		{
			for (ii = 1; ii < header[ll]->obstime->obsNum; ii++)
			{
				if (minLine < header[ll]->obstime->lineNo[ii])
				{
					data->startTime = header[ll]->obstime->obsMJD[ii - 1];
					break;
				}
				else if (minLine == header[ll]->obstime->lineNo[ii])
				{
					data->startTime = header[ll]->obstime->obsMJD[ii];
					break;
				}
			}
		}
		/* 4-2 endTime */
		if (startLine[ll] <= maxLine && maxLine <= endLine[ll])
		{
			for (ii = 1; ii < header[ll]->obstime->obsNum; ii++)
			{
				if (maxLine < header[ll]->obstime->lineNo[ii])
				{
					data->endTime = header[ll]->obstime->obsMJD[ii - 1];
				}
				else if (maxLine == header[ll]->obstime->lineNo[ii])
				{
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
	for (ii = 0; ii < arg->filenum; ii++)
	{
		if (header[ii] != NULL)
		{
			hisd_free(header[ii]);
		}
		if (fp[ii] != NULL)
		{
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
	return (NORMAL_END);
}

/* Write a file */
int write_file(char *file_name, outdata *data, parameter *param)
{
	std::ofstream outfile;

	const int height = (int)param->height;
	const int width = (int)param->width;
	const int bytes_per_pixel = 1;

	printf("Writing file with path %s\n", file_name);
	outfile.open(file_name, std::ios::out);
	
	for (int i = 0; i < height; i++)
	{
		for (int j = 0; j < width; j++)
		{
			int cur = i * width + j;
			outfile << data->phys[cur] << " ";
		}
		outfile << "\n";
	}
	outfile.close();
	return (NORMAL_END);
}

int main(int argc, char *argv[])
{

	/* 0. Variable */
	parameter param;
	argument arg;
	outdata data;
	long n_size;
	long ii;

	/* 1. Init Parameter */
	param.ltlat = atof((char *)argv[5]);
	param.ltlon = atof((char *)argv[6]);
	//param.ltlon = 100.4;
	param.width = PNGW;
	param.height = PNGH; // image.shape
	param.dlat = 0.0125; 
	param.dlon = 0.0125;

	printf("Left top (lat,lon) : (%6.2f,%6.2f)\n", param.ltlat, param.ltlon);
	printf("width,height       : (%6d,%6d)\n", param.width, param.height);
	printf("Spatial resolution : (%6.3f,%6.3f)\n", param.dlat, param.dlon);
	n_size = param.width * param.height;

	/* 2. Allocate */
	if (NULL == (data.phys = (float *)calloc(n_size, sizeof(float *))))
	{
		fprintf(stderr, "allocate error\n");
		return (ERROR_CALLOCATE);
	}
	/* init */
	for (ii = 0; ii < n_size; ii++)
	{
		data.phys[ii] = INVALID;
	}
	/* 3. ���ļ� */
	//update in 4.11

	//ԭ����
	/* 4. GetData && Make Png */
	arg.InFile[0] = (char *)argv[1];
	arg.InFile[1] = (char *)argv[2];
	arg.InFile[2] = (char *)argv[3];

	arg.filenum = 3;

	/* 4.2 ����getData����*/
	if (NORMAL_END != getData(&arg, &param, &data))
	{
		fprintf(stderr, "get data error\n");
		free(data.phys);
		return (ERROR_READ_DATA);
	}
	/* 4.3 Make File */
	write_file((char *)argv[4], &data, &param);
	printf("Write File Normal end..\n");
	/* 5. free */
	free(data.phys);

	/* 6. End */
	printf("NORMAL END\n");
	//return(NORMAL_END);
	return 0;
}