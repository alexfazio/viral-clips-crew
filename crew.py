# Standard library imports
import datetime
from datetime import datetime
import logging
import os
import sys
from textwrap import dedent

# Third party imports
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.chat_models import ChatOpenAI
# ↑ uncomment to use OpenAI API

# Local application imports
from crewai import Agent, Task, Crew, Process
import extracts  # Ensure this module is available and correctly imported

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use maskpass to prompt for the password and mask it with '*'
# gemini_api_key = maskpass.askpass(prompt="Enter GEMINI_API_KEY: ", mask="*")
#os.environ["GEMINI_API_KEY"] = gemini_api_key

gemini_api_key = os.getenv('GEMINI_API_KEY')

# Add API keys within `./.env` file
load_dotenv()


def main(extracts, subtitles):

    # Create the crew_output directory if it doesn't exist
    os.makedirs("crew_output", exist_ok=True)

    subtitler_agent_1 = Agent(
        role=dedent((
            f"""
            Segment 1 Subtitler
            """)),
        backstory=dedent((
            f"""
            Experienced subtitler who writes captions or subtitles that accurately represent the audio, including dialogue, sound effects, and music. The subtitles need to be properly timed with the video using correct time codes.
            """)),
        goal=dedent((
            f"""
            Match a list of extracts from a video clip with the corresponding timed subtitles. Given the segments found by the Digital Producer, find the segment timings within the `.srt` file and return each segment as an `.srt` subtitle segment.
            """)),
        allow_delegation=False,
        verbose=True,
        max_iter=1,
        max_rpm=1,
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest",
                                   verbose=True,
                                   temperature=0.5,
                                   google_api_key=gemini_api_key)
        # llm=ChatOpenAI(model_name="gpt-4", temperature=0.5)
        # ↑ uncomment to use OpenAI API + "gpt-4"
        # llm=ChatAnthropic(model='claude-3-opus-20240229', temperature=0.5),
        # ↑ uncomment to use Anthropic's API + "claude-3-opus-20240229"
        )

    subtitler_agent_2 = Agent(
        role=dedent((
            f"""
            Segment 2 Subtitler
            """)),
        backstory=dedent((
            f"""
            Experienced subtitler who writes captions or subtitles that accurately represent the audio, including dialogue, sound effects, and music. The subtitles need to be properly timed with the video using correct time codes.
            """)),
        goal=dedent((
            f"""
            Match a list of extracts from a video clip with the corresponding timed subtitles. Given the segments found by the Digital Producer, find the segment timings within the `.srt` file and return each segment as an `.srt` subtitle segment.
            """)),
        allow_delegation=False,
        verbose=True,
        max_iter=1,
        max_rpm=1,
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest",
                                   verbose=True,
                                   temperature=0.5,
                                   google_api_key=gemini_api_key)
        # llm=ChatOpenAI(model_name="gpt-4", temperature=0.5)
        # ↑ uncomment to use OpenAI API + "gpt-4"
        # llm=ChatAnthropic(model='claude-3-opus-20240229', temperature=0.5),
        # ↑ uncomment to use Anthropic's API + "claude-3-opus-20240229"
        )

    subtitler_agent_3 = Agent(
        role=dedent((
            f"""
            Segment 3 Subtitler
            """)),
        backstory=dedent((
            f"""
            Experienced subtitler who writes captions or subtitles that accurately represent the audio, including dialogue, sound effects, and music. The subtitles need to be properly timed with the video using correct time codes.
            """)),
        goal=dedent((
            f"""
            Match a list of extracts from a video clip with the corresponding timed subtitles. Given the segments found by the Digital Producer, find the segment timings within the `.srt` file and return each segment as an `.srt` subtitle segment.
            """)),
        allow_delegation=False,
        verbose=True,
        max_iter=1,
        max_rpm=1,
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest",
                                   verbose=True,
                                   temperature=0.5,
                                   google_api_key=gemini_api_key)
        # llm=ChatOpenAI(model_name="gpt-4", temperature=0.5)
        # ↑ uncomment to use OpenAI API + "gpt-4"
        # llm=ChatAnthropic(model='claude-3-opus-20240229', temperature=0.5),
        # ↑ uncomment to use Anthropic's API + "claude-3-opus-20240229"
    )

    return_subtitles_1 = Task(
        description=dedent((
            f"""
            You will be provided with a list of transcription extracts from a video clip, and the full content of an .srt subtitle file corresponding to that clip. Your task is to match each transcription extract to the subtitle segment it best aligns with, and return the results in a specific format.
        
            Here are the transcription extracts:
            <segments>
            {extracts[0]}
            </segments>
        
            And here is the full content of the .srt subtitle file:
            <srt_file>
            {subtitles}
            </srt_file>
        
            Please follow these steps:
            1. Carefully read through each transcription extract within the <segments> tags.
            2. For each extract, search through the <srt_file> content to find the subtitle segment that best matches the extract. To determine the best match, look for segments that contain the most overlapping words or phrases with the extract.
            3. Once you've found the best matching subtitle segment for an extract, format the match like this:
            [segment number]
            [start time] --> [end time] 
            [matched transcription extract]
        
            4. Repeat steps 1-3 for each transcription extract, keeping the extracts in the same order they appeared in the <segments> list.
            5. After processing all the extracts, combine the formatted matches into a single block of text. This should look like a valid .srt subtitle file, with each match separated by a blank line.
        
            Please note: .srt files have a specific format that must be followed exactly in order for them to be readable. Therefore, it is crucial that you do not include any extra content beyond the raw subtitle data itself. This means:
            - No comments explaining your work
            - No notes about which extracts matched which segments
            - No additional text that isn't part of the subtitle segments
        
            Simply return the matches, properly formatted, as the entire contents of your response.
            """)),
        expected_output=dedent((
            f"""
            Format each match exactly as follows, and include only these details:
        
            [segment number]
            [start time] --> [end time]
            [matched transcription extract]
        
            Compile all the matches and return them without any additional text or commentary.
        
            Example of the expected output:
        
            26
            00:01:57,000 --> 00:02:00,400
            Sight turned into insight.
            
            27
            00:02:00,400 --> 00:02:03,240
            Seeing became understanding.
            
            28
            00:02:03,240 --> 00:02:05,680
            Understanding led to actions,

        
            Please note: .srt files have a specific format that must be followed exactly in order for them to be readable. Therefore, it is crucial that you DO NOT INCLUDE any extra content beyond the raw subtitle data itself. This means:
            - No comments explaining your work
            - No comments introducing your work
            - No comments ending your work
            - No notes about which extracts matched which segments
            - No additional text that isn't part of the subtitle segments
            - No comments like: "Here is the output with the matched segments in the requested format:"
            """)),
        agent=subtitler_agent_1,
        output_file=f'crew_output/new_file_return_subtitles_1_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.srt'
    )

    return_subtitles_2 = Task(
        description=dedent((
            f"""
            You will be provided with a list of transcription extracts from a video clip, and the full content of an .srt subtitle file corresponding to that clip. Your task is to match each transcription extract to the subtitle segment it best aligns with, and return the results in a specific format.

            Here are the transcription extracts:
            <segments>
            {extracts[1]}
            </segments>

            And here is the full content of the .srt subtitle file:
            <srt_file>
            {subtitles}
            </srt_file>

            Please follow these steps:
            1. Carefully read through each transcription extract within the <segments> tags.
            2. For each extract, search through the <srt_file> content to find the subtitle segment that best matches the extract. To determine the best match, look for segments that contain the most overlapping words or phrases with the extract.
            3. Once you've found the best matching subtitle segment for an extract, format the match like this:
            [segment number]
            [start time] --> [end time] 
            [matched transcription extract]

            4. Repeat steps 1-3 for each transcription extract, keeping the extracts in the same order they appeared in the <segments> list.
            5. After processing all the extracts, combine the formatted matches into a single block of text. This should look like a valid .srt subtitle file, with each match separated by a blank line.

            Please note: .srt files have a specific format that must be followed exactly in order for them to be readable. Therefore, it is crucial that you do not include any extra content beyond the raw subtitle data itself. This means:
            - No comments explaining your work
            - No notes about which extracts matched which segments
            - No additional text that isn't part of the subtitle segments

            Simply return the matches, properly formatted, as the entire contents of your response.
            """)),
        expected_output=dedent((
            f"""
            Format each match exactly as follows, and include only these details:

            [segment number]
            [start time] --> [end time]
            [matched transcription extract]

            Compile all the matches and return them without any additional text or commentary.

            Example of the expected output:

            26
            00:01:57,000 --> 00:02:00,400
            Sight turned into insight.

            27
            00:02:00,400 --> 00:02:03,240
            Seeing became understanding.

            28
            00:02:03,240 --> 00:02:05,680
            Understanding led to actions,


            Please note: .srt files have a specific format that must be followed exactly in order for them to be readable. Therefore, it is crucial that you DO NOT INCLUDE any extra content beyond the raw subtitle data itself. This means:
            - No comments explaining your work
            - No comments introducing your work
            - No comments ending your work
            - No notes about which extracts matched which segments
            - No additional text that isn't part of the subtitle segments
            - No comments like: "Here is the output with the matched segments in the requested format:"
            """)),
            agent=subtitler_agent_2,
            # ↑ specify which task's output should be used as context for subsequent tasks
            output_file=f'crew_output/new_file_return_subtitles_2_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.srt'
        )

    return_subtitles_3 = Task(
        description=dedent((
            f"""
            You will be provided with a list of transcription extracts from a video clip, and the full content of an .srt subtitle file corresponding to that clip. Your task is to match each transcription extract to the subtitle segment it best aligns with, and return the results in a specific format.

            Here are the transcription extracts:
            <segments>
            {extracts[2]}
            </segments>

            And here is the full content of the .srt subtitle file:
            <srt_file>
            {subtitles}
            </srt_file>

            Please follow these steps:
            1. Carefully read through each transcription extract within the <segments> tags.
            2. For each extract, search through the <srt_file> content to find the subtitle segment that best matches the extract. To determine the best match, look for segments that contain the most overlapping words or phrases with the extract.
            3. Once you've found the best matching subtitle segment for an extract, format the match like this:
            [segment number]
            [start time] --> [end time] 
            [matched transcription extract]

            4. Repeat steps 1-3 for each transcription extract, keeping the extracts in the same order they appeared in the <segments> list.
            5. After processing all the extracts, combine the formatted matches into a single block of text. This should look like a valid .srt subtitle file, with each match separated by a blank line.

            Please note: .srt files have a specific format that must be followed exactly in order for them to be readable. Therefore, it is crucial that you do not include any extra content beyond the raw subtitle data itself. This means:
            - No comments explaining your work
            - No notes about which extracts matched which segments
            - No additional text that isn't part of the subtitle segments

            Simply return the matches, properly formatted, as the entire contents of your response.
            """)),
        expected_output=dedent((
            f"""
            Format each match exactly as follows, and include only these details:

            [segment number]
            [start time] --> [end time]
            [matched transcription extract]

            Compile all the matches and return them without any additional text or commentary.

            Example of the expected output:

            26
            00:01:57,000 --> 00:02:00,400
            Sight turned into insight.

            27
            00:02:00,400 --> 00:02:03,240
            Seeing became understanding.

            28
            00:02:03,240 --> 00:02:05,680
            Understanding led to actions,


            Please note: .srt files have a specific format that must be followed exactly in order for them to be readable. Therefore, it is crucial that you DO NOT INCLUDE any extra content beyond the raw subtitle data itself. This means:
            - No comments explaining your work
            - No comments introducing your work
            - No comments ending your work
            - No notes about which extracts matched which segments
            - No additional text that isn't part of the subtitle segments
            - No comments like: "Here is the output with the matched segments in the requested format:"
            """)),
        agent=subtitler_agent_3,
        # ↑ specify which task's output should be used as context for subsequent tasks
        output_file=f'crew_output/new_file_return_subtitles_3_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.srt'
    )

    # TODO: ↓ set `verbose` to false after debug

    crew = Crew(
        agents=[subtitler_agent_1, subtitler_agent_2, subtitler_agent_3],
        tasks=[return_subtitles_1, return_subtitles_2, return_subtitles_3],
        verbose=2,  # You can set it to 1 or 2 to different logging levels
        # ↑ indicates the verbosity level for logging during execution.
        process=Process.sequential,
        # ↑ the process flow that the crew will follow (e.g., sequential, hierarchical).
        # manager_agent=manager,
    )

    result = crew.kickoff()
    logging.info(dedent(f"""\n\n########################"""))
    logging.info(dedent(f"""## Here is your custom crew run result:"""))
    logging.info(dedent(f"""########################\n"""))
    logging.info(result)

    return result


if __name__ == "__main__":

    # Check if the whisper_output directory exists and contains .srt and .txt files
    whisper_output_dir = 'whisper_output'
    
    if os.path.exists(whisper_output_dir):
        srt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.srt')]
        txt_files = [f for f in os.listdir(whisper_output_dir) if f.endswith('.txt')]

        if srt_files and txt_files:
            # Assuming the first .srt and .txt files are the ones to process
            subtitles_file = os.path.join(whisper_output_dir, srt_files[0])
            transcript_file = os.path.join(whisper_output_dir, txt_files[0])

            with open(transcript_file, 'r') as file:
                transcript = file.read()

            with open(subtitles_file, 'r') as file:
                subtitles = file.read()

            # Ensure extracts.main() returns the expected data and waits for it to finish
            extracts_data = extracts.main()
            while extracts_data is None:
                extracts_data = extracts.main()

            main(extracts_data, subtitles)
        else:
            logging.warning("No .srt or .txt files found in the whisper_output directory.")
    else:
        logging.info(f"Directory not found: {whisper_output_dir}")
        sys.exit(1)
