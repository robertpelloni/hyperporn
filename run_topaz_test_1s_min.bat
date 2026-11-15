@echo off
set "TVAI_MODEL_DIR=C:\Users\hyper\workspace\hyperporn\topaz-models-min"
set "TVAI_MODEL_DATA_DIR=C:\Users\hyper\workspace\hyperporn\topaz-models"
set "PATH=C:\Users\hyper\workspace\hyperporn\topaz-extract\PFiles\Topaz Labs LLC\Topaz Video;%PATH%"
"C:\Users\hyper\workspace\hyperporn\topaz-extract\PFiles\Topaz Labs LLC\Topaz Video\ffmpeg.exe" -hide_banner -loglevel verbose -y -i topaz_test_src_1s.mp4 -vf tvai_up=model=prob-4:scale=0:w=3840:h=2160:device=-1 -c:v hevc_qsv -global_quality 16 -r 60 topaz_test_1s_4k.mp4 2> topaz_test_1s_min.log
echo TOPAZ_EXIT=%ERRORLEVEL%
type topaz_test_1s_min.log
