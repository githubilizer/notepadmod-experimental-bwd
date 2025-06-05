#!/usr/bin/env python3

# /modules/ts2.py

# How to use: python3 cleanerAI_v1.py inputfile.vhd
# This script updates the input file in place after creating a backup.

# This script cleans up a rough draft

# FILENAME CHANGED TO ts2.py

import sys
import argparse
import re
import os
import shutil
import time  # For timestamp
import threading
import itertools
from openai import OpenAI  # Updated import syntax
import logging

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ELECTRIC_BLUE = "\033[38;2;44;117;255m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"  # Added reset color code

# Set your OpenAI API key securely using an environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Updated API KEY syntax

def setup_logging():
    """Configure logging settings."""
    logging.basicConfig(
        filename='/home/j/Desktop/code/notepadMOD/logs/cleanerAI_ts2.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_segments_with_positions(content):
    """
    Extract segments that are between lines containing only '222', along with their positions.
    """
    pattern = r'(222\s*\n(.*?)\n\s*222)'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    segments = []
    for match in matches:
        full_match = match.group(1)
        segment_content = match.group(2)
        start = match.start()
        end = match.end()
        segments.append({'full_match': full_match, 'content': segment_content, 'start': start, 'end': end})
    logging.info(f"Parsed {len(segments)} segments.")
    print(f"[INFO] Parsed {len(segments)} segments.")
    return segments

def clean_segment(segment, window=None):
    """
    Process the text segment using OpenAI's LLM with the specified instruction.

    Returns:
    - processed_text (str): The text generated according to the new instruction.
    """
    try:
        # Prepare the instruction prompt
        instructions = (
            """
Create 1 long sentence of a concise and cohesive update from multiple seemingly unrelated tweets that are actually about the same single event. "
    "Carefully connect the details while ensuring clarity, avoiding repetition, and providing proper context. "
    "Ensure towns and regions are accurately distinguished to prevent location confusion. "
    "1) Avoid redundancy: Don’t repeat the same information across different updates. If a governor reports the same number of UAVs being shot down in multiple posts, combine the info in a single sentence, and don't restate it unless there’s new context. "
    "2) Tone: Keep the tone casual but sharp, with some dry humor or light sarcasm where appropriate, but stick to the facts. This is not the place for sensationalism—focus on real-time updates without over-dramatizing. "
    "3) Precision over generalities: Avoid vague phrases and abstract phrases like the following: tensions rise, the situation unfolds, The situation has drawn significant attention. "
    "   ii) If there's a tangible update, such as reports of explosions, focus on that, and don't fall back on generalizations. "
    "4) Concise updates: Each part of the update should be no more than 3-4 sentences long. Break the event into key points, covering the air defense response, actions by local authorities, and resident reports, with a focus on what is confirmed and what is happening right now. "
    "5) Key details: When citing facts, ensure clarity in distinguishing between the town and region/Oblast, especially when talking about separate events in different parts of the same location. "
    "6) Don't mention information about civilians wounded or civilian casualties in your output. "
    "7) If there's not enough context, then don't create an output. "
    "Additionally, emulate the following writing style based on the provided examples:\n\n"
    "• Casual but sharp tone with dry humor or light sarcasm.\n"
    "• Specific formatting with bullet points and clear segmentation.\n"
    "• Focus on detailed factual reporting without sensationalism.\n"
    "• Incorporate in-depth analysis and contextual information.\n"
    "• Maintain a conversational flow while ensuring clarity and precision.\n"
    "• Avoid redundancy and ensure each update provides unique value.\n"
    "• Stick to 2 long sentences at most of news bite-sized output in a flowing narrative.\n\n"
    "Additionally, incorporate the following vocabulary and phrases to enhance the narrative style and precision:\n\n"
    "• that lacked sufficient field concealment\n"
    "• engulfing approximately 1,500 square meters\n"
    "• preserving the lives of\n"
    "• where these events unfolded\n"
    "• compensate\n"
    "• to supplement its artillery capabilities\n"
    "• shot down Russian cruise missiles in this configuration\n"
    "• the Russian armored vehicles attempted to disperse\n"
    "• in the steppes of Donetsk\n"
    "• refinery was ravaged to drones\n"
    "• stemming directly from\n"
    "• coordinating these operations\n"
    "• on social media accounts dryly noting that the consequences of invading a neighbor can come back to haunt you\n"
    "• signifies a substantial shift\n"
    "• Real estate market woes continue to surface\n"
    "• Additionally, caught in the lens of a Ukrainian reconnaissance drone\n"
    "• that showcased its capabilities\n"
    "• a significant inflection point in strike capabilities\n"
    "• a critical hit\n"
    "• drunken defeatist mindset\n"
    "• business is running at a loss, leading them to self-immolate the plant.\n"
    "• This event highlights the ongoing resistance within the region, and while details remain limited, this act underscores the growing resolve among those opposing the current regime.\n"
    "• considerable pace\n"
    "• stave off\n"
    "• this is the antithesis of winning\n"
    "• to avoid theft of the much coveted item\n"
    "• kicking the can down the road\n"
    "• conducted a series of strikes against enemy positions\n"
    "• with each platform designed for their own specific mission profile needs\n"
    "• strengthening ties between\n"
    "• as a significant fire engulfed abz/xyz\n"
    "• over-utilisation\n"
    "• in part due to the over-utilization of the network compounded by limited maintenance and spare parts, as a result of a heavily sanctioned yet vital industry of Russia's\n"
    "• Ukrainian Defense Forces launched a powerful counterattack near the village of Pishchane, compelling Russian troops to retreat.\n"
    "• destroyed a bridge over the Solona River, hampering enemy movements.\n"
    "• A disillusioned Russian soldier\n"
    "• drop in the bucket\n"
    "• if only they can figure out how to properly get the desired utility of them\n"
    "• Silencing those voices of opposition\n"
    "• Kremlin mouthpiece\n"
    "• remnants\n"
    "• yep. that's the depths of calculated deception and systemic fraud at work in Russia.\n"
    "• Proliferation\n"
    "• Propagation\n"
    "• significant challenges\n"
    "• prohibitively\n"
    "• Rostov reports another restless night\n"
    "• but this level of diminished output\n"
    "• Deterrent\n"
    "• critically\n"
    "• a country rich in natural resources\n"
    "• only to meet an ill fate\n"
    "• incorporate\n"
    "• Coinciding with\n"
    "• At a commensurate rate\n"
    "• Used to aid in carrying Russian troops to front lines of war.\n"
    "• Gabmit\n"
    "• garrison\n"
    "• hallmarks of a ... abc\n"
    "• Critical\n"
    "• coming to us courtesy of a\n"
    "• Probe\n"
    "• with particular emphasis\n"
    "• on the first word there,\n"
    "• continues to be a painful thorn for Moscow\n"
    "• coverage\n"
    "• then immediately south of this location\n"
    "• as a means to inflict the most destruction\n"
    "• excruciatingly essential\n"
    "• home to Russia's Caspian Sea flotilla\n"
    "• insufficiencies\n"
    "• was within safe retrieval proximity\n"
    "• impenetrable\n"
    "• Participants\n"
    "• compliance\n"
    "• skyrocketing prices\n"
    "• launched some distance from the front line, though was likely launched from even further afield.\n"
    "• trade blows\n"
    "• with mass scarcity\n"
    "• blatantly obvious\n"
    "• we see the proliferation of\n"
    "• has not been able to dislodge Ukraine from the territory.\n"
    "• leading to some unhealthy levels of cognitive dissonance\n"
    "• incapacitated\n"
    "• when entering the gauntlet\n"
    "• A grim new testament\n"
    "• with a seemingly limited awareness of this situation of impending doom.\n"
    "• stringent adherence\n"
    "• to oust the AFU\n"
    "• unprecedented levels of frontline activity\n"
    "• from which to launch their offensives with\n"
    "• fostering\n"
    "• topping the list at\n"
    "• the plot thickens\n"
    "• coalesce\n"
    "• aerial threats\n"
    "• as a means to suppress\n"
    "• sustained\n"
    "• Then to Kursk, because my-o-my\n"
    "• threshold\n"
    "• The aftermath of the disaster has plunged the Russians into a logistical nightmare\n"
    "• detailing the\n"
    "• Ukraine has become a hotbed of defense innovation as it rapidly develops new battlefield technologies\n"
    "• shared their harrowing story\n"
    "• an attempted reinvigoration of Russian offensive operations\n"
    "• no additional information has been revealed.\n"
    "• a significant contribution\n"
    "• for the region, in precision fashion\n"
    "• colossal fire\n"
    "• which have already proven invaluable for Ukraine\n"
    "• will often be equipped with\n"
    "• visuals from the scene showed several infernos\n"
    "• The initial operational tempo had the Russian forces\n"
    "• leading to a flow on ripple effect\n"
    "• temperatures will plummet\n"
    "• the Russian military is looking to facilitate\n"
    "• unabated\n"
    "• the debilitating muddy season of rasputitsa\n"
    "• all of which has been met with fierce Ukrainian opposition\n"
    "• decrepit aircraft carrier\n"
    "• decrepit\n"
    "• bludgeoning\n"
    "• ultra modern warfare\n"
    "• infuriating the commander\n"
    "• ineptitude\n"
    "• And then most accurately on map,\n"
    "• combatant\n"
    "• warranting additional\n"
    "• motivating factor\n"
    "• but a strike like this is clearly designed to disrupt Russian railway logistics\n"
    "• of questionable salvage\n"
    "• tried to downplay the sheer undeniable significance of the event\n"
    "• as they target military objects inside of Russia\n"
    "• Of course we see already a recent and massive uptick\n"
    "• opportunistic behavior\n"
    "• making it even more appealing\n"
    "• Color me shocked\n"
    "• been in the throws of\n"
    "• somewhere in this embattled zone.\n"
    "• lull them into a false sense of security\n"
    "• Russian commanders are throwing away their troops in performative assaults to impress their superiors\n"
    "• contend with\n"
    "• becoming increasingly skilled in this arena\n"
    "• so pervasive\n"
    "• who shares a more candid report\n"
    "• fantastical\n"
    "• elaborates\n"
    "• But very crucially also\n"
    "• Demonstrates\n"
    "• theme\n"
    "• transparency\n"
    "• recipients\n"
    "• containment\n"
    "• diminished the need for\n"
    "• cauldron\n"
    "• the rapid proliferation of\n"
    "• probing\n"
    "• could be attributed to\n"
    "• across the board\n"
    "• critical mass\n"
    "• the operational needle hasn't moved much\n"
    "• tipping point\n"
    "• breaking point\n"
    "• materialize\n"
    "• waiting for the perfect alignment on conditions\n"
    "• their very deeply embedded mindset\n"
    "• their massive proliferation\n"
    "• the fallacy\n"
    "• gargantuan\n"
    "• additional reports surface\n"
    "• foreshadowing\n"
    "• barren desolate wasteland\n"
    "• untenable\n"
    "• Russian elements (Russian military personnel)\n"
    "• hamlet\n"
    "• further disrupting Russian lines between\n"
    "• Ukrainian advancements\n"
    "• which has a broad appeal\n"
    "• to support its forward operating positions\n"
    "• Russia claimed\n"
    "• PREDOMINANTLY\n"
    "• coordinated drone strike\n"
    "• then to the eastern segment\n"
    "• the Kherson operational direction\n"
    "• with just the northern attack vector being exploited at this stage\n"
    "• as revealed by\n"
    "• demonstrates\n"
    "• devastating impact\n"
    "• The charred remains of a\n"
    "• they clearly played down the significance of this event.\n"
    "• well positioned\n"
    "• Disgraceful\n"
    "• a new trend emergence\n"
    "• Discovered\n"
    "• quite significant\n"
    "• where the contact point lines have been more or less drawn for weeks now.\n"
    "• This activity\n"
    "• consolidated positions\n"
    "• sustained efforts\n"
    "• intention\n"
    "• Frequent\n"
    "• Rampant\n"
    "• Intentional\n"
    "• objective\n"
    "• Deliberate\n"
    "• Purposeful\n"
    "• an alarming trend\n"
    "• reveals\n"
    "• Czar Putin\n"
    "• entitled\n"
    "• so it's a scathing indictment of logistical incompetence\n"
    "• from existing stocks or inventory\n"
    "• resorted to\n"
    "• preserving\n"
    "• determines\n"
    "• severely\n"
    "• incompetence\n"
    "• uncontested Juggernaut\n"
    "• criticism\n"
    "• challenges\n"
    "• serious\n"
    "• satellite images have emerged\n"
    "• of the adversary\n"
    "• with the introduction of\n"
    "• As Russia's mainstay tactic is to try to over-match Ukrainian positions with mass\n"
    "• the author's summary can be distilled to\n"
    "• may indicate some limited momentum toward\n"
    "• compared to\n"
    "• marginal area of control losses for Russia\n"
    "• further eroding Russia's connection to the abc location\n"
    "• ensuing cloud of smoke\n"
    "• covert\n"
    "• highlighting a shift in tactical thinking\n"
    "• bizarrely\n"
    "• squandered\n"
    "• Conducted\n"
    "• initiated\n"
    "• with the recon UAVs being the perfect real-time tool to relay coordinates of such high-value targets back to the rocket artilleryists\n"
    "• the level of impact\n"
    "• Initiative\n"
    "• focus their defensive military efforts\n"
    "• to supplement\n"
    "• remains\n"
    "• fireworks spitting out of\n"
    "• entirely plausible\n"
    "• Probe Infantry - aka reconnaissance-in-force actions.\n"
    "• This is a scathing indictment of the Russian army's failure to provide basic necessities for its troops.\n"
    "• to use it as a sufficient base or springboard in which to launch further ground attacks with\n"
    "• strategic location\n"
    "• and almost nothing else on the field (bar an ammunition depot) goes up in flames, quite like this\n"
    "• like this IFV.\n"
    "• deficit\n"
    "• strategic necessitation\n"
    "• who have an almost unquenchable thirst for invasion\n"
    "• campaign\n"
    "• implemented\n"
    "• Performant\n"
    "• signify\n"
    "• frequently\n"
    "• that invariably leads to\n"
    "• an atrocious lack of maintenance\n"
    "• expand\n"
    "• momentum\n"
    "• atomized\n"
    "• inflationary repercussions\n"
    "• emerging from its\n"
    "• encapsulation\n"
    "• vulnerability\n"
    "• designed to engage low-altitude threats\n"
    "• determine\n"
    "• activity\n"
    "• diminished\n"
    "• thus an innovative approach to military equipment acquisitions\n"
    "• lost their dominance in the Black Sea for the foreseeable future\n"
    "• sustain\n"
    "• He is quote unquote an expert on the subject\n"
    "• to achieve such an objective\n"
    "• definitively\n"
    "• to the exclusion of\n"
    "• misconceptions\n"
    "• mitigate\n"
    "• showcasing\n"
    "• in the adjacent pocket\n"
    "• disrupting\n"
    "• obfuscate\n"
    "• inadvertently\n"
    "• in very limited volume\n"
    "• vulnerable\n"
    "• susceptible\n"
    "• INTRIGUINGLY\n"
    "• Otherwise, they'll just face consequences for\n"
    "• damage assessment\n"
    "• with the implications of such an event being that this will further strategically position the AFU to collapse the most southern Russian positions within the region\n"
    "• reputational damage\n"
    "• plunged into\n"
    "• this approach\n"
    "• old hardware reactivated\n"
    "• old hardware reactivation\n"
    "• advancing formation\n"
    "• the internationally recognized Ukrainian border\n"
    "• reckless negligence\n"
    "• irrevocable\n"
    "• just barely getting away unscathed\n"
    "• which would appear to relate to these latest developments\n"
    "• close quarters combat\n"
    "• the Kremlin's mouthpieces\n"
    "• plausible\n"
    "• plausibly\n"
    "• some level of partisan activity known to be present\n"
    "• coupled with\n"
    "• related to\n"
    "• as evidenced by\n"
    "• thereby minimizing its exposure, decreasing its targetable footprint.\n"
    "• shortfall\n"
    "• Large case\n"
    "• indicates\n"
    "• as it marks an approximation of\n"
    "• intimidation\n"
    "• mitigate the threat\n"
    "• harvesting\n"
    "• As we saw a new iteration of\n"
    "• field gun\n"
    "• incarceration\n"
    "• using a tree line for cover\n"
    "• these monstrous concoctions\n"
    "• a Ukrainian unit\n"
    "• at an inflection point\n"
    "• minimizing the need for\n"
    "• to pave the way for\n"
    "• with different mission profiles\n"
    "• intensifies\n"
    "• targeted\n"
    "• deliberate choice of target\n"
    "• the plight\n"
    "• halted\n"
    "• the key differentiator\n"
    "• performed\n"
    "• orchestrated\n"
    "• enacted\n"
    "• provisions\n"
    "• utility\n"
    "• harrowing\n"
    "• Russian accounts also reveal that\n"
    "• lenient\n"
    "• concerted frontline efforts\n"
    "• trending\n"
    "• disrupt and degrade\n"
    "• positioned on top\n"
    "• pitfalls\n"
    "• full utilization\n"
    "• marred by delays\n"
    "• sufficiently\n"
    "• aspirations\n"
    "• to undermine the economic foundations supporting Russia's war.\n"
    "• stand up for a nation's sovereignty, upholding the principles of freedom and self-determination against any form of aggression\n"
    "• border conflict zones\n"
    "• MARKS a significant POINT inflection in Ukraine's demonstrated capability\n"
    "• SHOWCASES\n"
    "• CRUCIAL/Y\n"
    "• CATASTROPHIC\n"
    "• DEVASTATINGLY\n"
    "• STAGGERING\n"
    "• At best\n"
    "• MONSTROUSLY\n"
    "• MONSTROSITY\n"
    "• DEVASTATING BLOWS\n"
    "• inextricably\n"
    "• UTTERLY DECIMATED\n"
    "• FEROCIOUSLY\n"
    "• THE WHOLE GAMUT / THE FULL GAMUT\n"
    "• AFU spectacularly destroyed\n"
    "• ABSOLUTELY DISASTROUS\n"
    "• DESTROYED IN AN INFERNAL BLAZE after a\n"
    "• HIMARS GMLRS round\n"
    "• BUT WITH THE INCREASED REGULARITY OF\n"
    "• visited them.\n"
    "• VAPORIZED\n"
    "• HORRIFICALLY MASSIVE\n"
    "• WHICH ARE COMPLETELY OUTDATED FOR THE TASK AT HAND\n"
    "• DUE TO WESTERN IMPOSED ECONOMIC SANCTIONS, RUSSIA'S MILITARY INDUSTRY HAS REGRESSED SIGNIFICANTLY.\n"
    "• ATROCIOUS ACCURACY\n"
    "• Most of Russians fell into apathy, accepting their fate as sheep to the slaughter\n"
    "• Ukrainian defenders WOULD face mounting pressure to maintain their hold on these key positions.\n"
    "• IN AN ATTEMPT TO SECURE MORE LAND\n"
    "• PREDICTABILITY.\n"
    "• undermine\n"
    "• with fierce battles ongoing\n"
    "• and provide assistance on an expedited basis\n"
    "• clashes\n"
    "• intensity\n"
    "• antagonism\n"
    "• vitriol\n"
    "• subsequently\n"
    "• IN ANOTHER INCREMENTAL YET CRIPPLING BLOW TO RUSSIA'S AIR DEFENSE CAPABILITIES, EXPOSING VULNERABILITIES IN THEIR PROTECTIVE UMBRELLA.\n"
    "• MOVE EAST TO SAFELY MAINTAIN THEIR PRESENCE\n"
    "• equipped\n"
    "• make it to act as a force multiplier\n"
    "• they appear to have some utility\n"
    "• given the lack of protection afforded to\n"
    "• Addressing a potential demographic collapse\n"
    "• capitalize\n"
    "• on Ukrainian soil\n"
    "• is to overstate your capabilities\n"
    "• The Institute for the Study of War assesses that\n"
    "• has sought to utilize\n"
    "• resulting from\n"
    "• what we have here\n"
    "• which is a very important instrument for which Russia wages its war with\n"
    "• Insanely\n"
    "• Mercenaries\n"
    "• Abroad\n"
    "• cohort\n"
    "• curtail\n"
    "• sensationalist claims\n"
    "• not a panacea\n"
    "• fueling speculation about\n"
    "• brandishing\n"
    "• nomenclature\n"
    "• misnomer\n"
    "• Strong-armed\n"
    "• impunity\n"
    "• force multiplication effect\n"
    "• circumvent\n"
    "• shortfall falls\n"
    "• without impunity\n"
    "• new details emerge about\n"
    "• it's patently absurd that\n"
    "• Nonetheless\n"
    "• is not a silver bullet\n"
    "• disappointment is palpable\n"
    "• rife with inaccuracies\n"
    "• mince meat\n"
    "• Most perplexing however is that\n"
    "• orders of magnitude\n"
    "• led by the nose (to be easily controlled or manipulated by someone else, often without realizing it).\n"
    "• underscoring the strain on their conventional resources.\n\n"
    "Please apply all the above guidelines to rewrite 1 long sentence:\n\n"
"""
        )

        print("[INFO] Connecting to OpenAI API to process the segment...")
        logging.info("[INFO] Connecting to OpenAI API to process the segment...")

        if window:
            window.statusBar().showMessage("Sending request to OpenAI API...")

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated model
            messages=[
                {"role": "user", "content": instructions.format(segment=segment)},
            ],
            max_tokens=300,  # Adjust as needed
            n=1,
            stop=None,
            temperature=0
        )

        # Extract the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()

        # Log and print the raw API response
        print(f"[INFO] OpenAI API response: {assistant_reply}")
        logging.info(f"OpenAI API response: {assistant_reply}")

        if window:
            window.statusBar().showMessage("AI processing completed successfully!", 5000)

        return assistant_reply

    except Exception as e:
        error_message = f"Error processing segment: {e}"
        print(f"[ERROR] {error_message}")
        logging.error(error_message)
        
        if window:
            window.statusBar().showMessage(f"Error during AI processing: {str(e)}", 5000)
        
        # On error, return the original segment
        return segment

def main():
    setup_logging()
    logging.info("Script started.")
    print("[INFO] Script started.")

    # Check if the OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        error_message = "OpenAI API key is not set. Please set the 'OPENAI_API_KEY' environment variable."
        print(f"{RED}[ERROR] {error_message}{RESET}")
        logging.error(error_message)
        sys.exit(1)

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process and update segments in the input file.")
    parser.add_argument('input_file', help='Path to the input text file.')
    args = parser.parse_args()

    input_file = args.input_file

    # Read the input file
    try:
        print(f"[INFO] Reading input file '{input_file}'...")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        logging.info(f"Read input file '{input_file}' successfully.")
        print(f"[INFO] Read input file '{input_file}' successfully.")
    except FileNotFoundError:
        logging.error(f"Input file '{input_file}' not found.")
        print(f"{RED}[ERROR] Input file '{input_file}' not found.{RESET}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        print(f"{RED}[ERROR] Error reading input file: {e}{RESET}")
        sys.exit(1)

    # Create a backup of the input file in the specified directory with timestamp
    try:
        # Get the base filename without the path
        base_filename = os.path.basename(input_file)
        # Remove the extension from the filename
        filename_without_ext = os.path.splitext(base_filename)[0]
        # Get the current time in 12-hour format with am/pm
        time_str = time.strftime("%I%M%p").lower()
        # Remove leading zero from hour if present
        if time_str.startswith('0'):
            time_str = time_str[1:]

        # Construct the backup filename
        backup_filename = f"{filename_without_ext}_222_{time_str}.vhd"
        # Specify the backup directory
        backup_directory = "/home/j/Desktop/Finals/"
        # Ensure the backup directory exists
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        # Full backup path
        backup_file = os.path.join(backup_directory, backup_filename)
        # Copy the input file to the backup location
        shutil.copyfile(input_file, backup_file)
        logging.info(f"Created backup file '{backup_file}'.")
        print(f"[INFO] Created backup file '{backup_file}'.")
    except Exception as e:
        logging.error(f"Error creating backup file: {e}")
        print(f"{RED}[ERROR] Error creating backup file: {e}{RESET}")
        sys.exit(1)

    # Parse the segments with positions
    segments = parse_segments_with_positions(content)

    if not segments:
        warning_message = "No segments found between '222' markers. Please check the input file."
        print(f"{YELLOW}[WARNING] {warning_message}{RESET}")
        logging.warning(warning_message)
        sys.exit(1)

    # Initialize new content parts
    new_content_parts = []
    last_end = 0

    print("[INFO] Starting to process and update segments...")
    for idx, segment in enumerate(segments, 1):
        print(f"[INFO] Processing segment {idx}...")

        # Append content before the segment starts
        new_content_parts.append(content[last_end:segment['start']])

        # Process the segment with the new instruction
        updated_content = clean_segment(segment['content'])

        # Build the inserted updated segment with appropriate newlines
        inserted_content = '\n\n' + updated_content + '\n\n'

        # Append the inserted content **in place of** the original segment and '222' markers
        new_content_parts.append(inserted_content)

        # Update last_end to the end of the current segment
        last_end = segment['end']

    # Append any remaining content after the last segment
    new_content_parts.append(content[last_end:])

    # Reconstruct the new content
    new_content = ''.join(new_content_parts)

    # Write back to the input file
    try:
        print(f"[INFO] Writing back to the input file '{input_file}'...")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logging.info(f"Updated '{input_file}' successfully.")
        print(f"{GREEN}[INFO] Updated {ELECTRIC_BLUE}'{input_file}' {GREEN}successfully.{RESET}")
    except Exception as e:
        logging.error(f"Error writing to input file: {e}")
        print(f"{RED}[ERROR] Error writing to input file: {e}{RESET}")
        sys.exit(1)

    print(f"{GREEN}[INFO] Script completed successfully.{RESET}")

if __name__ == "__main__":
    main()

