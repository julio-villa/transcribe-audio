This script uses the whisper library from OpenAI to transcribe audio. It bypasses the 25mb file size limit by splitting larger files into smaller chunks and transcribing them separately, then joining the transcriptions. To use, navigate to the directory in which the script is located in, and run the following command:
```
python main.py path_to_audio_file output_text_file
```
For example:
```
python main.py audio_file.wav transcription.txt
```
