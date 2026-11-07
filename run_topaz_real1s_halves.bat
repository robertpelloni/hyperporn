@echo off
set "TVAI_MODEL_DIR=C:\Users\hyper\workspace\hyperporn\topaz-models-min"
set "TVAI_MODEL_DATA_DIR=C:\Users\hyper\workspace\hyperporn\topaz-models"
set "PATH=C:\Users\hyper\workspace\hyperporn\topaz-extract\PFiles\Topaz Labs LLC\Topaz Video;%PATH%"
set "TVFF=C:\Users\hyper\workspace\hyperporn\topaz-extract\PFiles\Topaz Labs LLC\Topaz Video\ffmpeg.exe"
"%TVFF%" -hide_banner -loglevel verbose -y -i topaz_test_src_1s.mp4 -frames:v 30 -vf tvai_up=model=prob-4:scale=0:w=3840:h=2160:device=-1,scale=3840:2160:flags=lanczos,format=nv12 -c:v hevc_qsv -global_quality 16 -r 60 -movflags frag_keyframe+empty_moov+default_base_moof -flush_packets 1 topaz_real1s_A.mp4 2> topaz_real1s_A.log
echo HALF_A_EXIT=%ERRORLEVEL%
"%TVFF%" -hide_banner -loglevel verbose -y -ss 0.5 -i topaz_test_src_1s.mp4 -frames:v 30 -vf tvai_up=model=prob-4:scale=0:w=3840:h=2160:device=-1,scale=3840:2160:flags=lanczos,format=nv12 -c:v hevc_qsv -global_quality 16 -r 60 -movflags frag_keyframe+empty_moov+default_base_moof -flush_packets 1 topaz_real1s_B.mp4 2> topaz_real1s_B.log
echo HALF_B_EXIT=%ERRORLEVEL%
(echo file 'topaz_real1s_A.mp4' & echo file 'topaz_real1s_B.mp4') > topaz_real1s_concat.txt
"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe" -hide_banner -y -f concat -safe 0 -i topaz_real1s_concat.txt -c copy -movflags +faststart topaz_test_real1s_4k.mp4 2> topaz_real1s_concat.log
echo CONCAT_EXIT=%ERRORLEVEL%
