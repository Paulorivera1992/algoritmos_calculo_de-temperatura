LIB = -lm -ltiff

all: direct rec_spect

direct: Tf_direct.c
	gcc Tf_direct.c -o Tf_direct $(LIB)

rec_spect: Tf_rec_spect.c
	gcc Tf_rec_spect.c -o Tf_rec_spect $(LIB)

clean:
	rm -f Tf_direct Tf_rec_spect

