import os
import whisper
from pydub import AudioSegment
import argparse

def split_audio(file_path, max_size_mb=25):
    audio = AudioSegment.from_file(file_path)

    # Calculate the maximum duration of each chunk in milliseconds
    bytes_per_millisecond = len(audio.raw_data) / len(audio)
    max_chunk_size_bytes = max_size_mb * 1024 * 1024
    max_duration_ms = int(max_chunk_size_bytes / bytes_per_millisecond)

    chunks = []
    for start_ms in range(0, len(audio), max_duration_ms):
        end_ms = start_ms + max_duration_ms
        if end_ms > len(audio):
            end_ms = len(audio)
        chunks.append(audio[start_ms:end_ms])
    return chunks


def transcribe_chunk(chunk, start_ms, model="base"):
    chunk_file = "temp_chunk.wav"
    chunk.export(chunk_file, format="wav")

    model = whisper.load_model(model)
    result = model.transcribe(chunk_file)

    # Format the start time as HH:MM:SS
    hours, remainder = divmod(start_ms // 1000, 3600)
    minutes, seconds = divmod(remainder, 60)
    timestamp = f"{hours:02}:{minutes:02}:{seconds:02}"

    os.remove(chunk_file) 

    # Basic formatting of the transcription text
    formatted_text = format_transcription(result['text'])

    # Return the transcription with the timestamp
    return f"[{timestamp}] {formatted_text}"

def format_transcription(text, char_limit=100):
    """
    Inserts a newline character approximately every `char_limit` characters.
    Attempts to break at sentence endings for better readability.
    """
    words = text.split()
    formatted_text = ""
    line_length = 0

    for word in words:
        formatted_text += word + " "
        line_length += len(word) + 1

        if line_length >= char_limit and word.endswith('.'):
            formatted_text += "\n"
            line_length = 0

    return formatted_text



def transcribe_audio(file_path):
    if os.path.getsize(file_path) > 25 * 1024 * 1024:
        chunks = split_audio(file_path)
        transcriptions = []
        for i, chunk in enumerate(chunks):
            start_ms = i * (len(chunk) / len(chunk.raw_data)) * len(chunk.raw_data)
            transcriptions.append(transcribe_chunk(chunk, start_ms))
    else:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        transcriptions = [result["text"]]
    
    return "\n".join(transcriptions)


def main(audio_file_path, output_file_path):
    transcription = transcribe_audio(audio_file_path)
    with open(output_file_path, "w") as file:
        file.write(transcription)
    print(f"Transcription saved to {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe Audio File")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("output_file", help="Path to the output text file")
    args = parser.parse_args()

    main(args.audio_file, args.output_file)
