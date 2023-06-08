import re

def main():
    while True:
        print(processingـincomingـmessages(input("Message: ")))
    

def processingـincomingـmessages(text):
        match = re.search(r"^(ferment)\b.*\b(set \w*)\b.*\-\s*(\d*)", text)
        if match:
            try:
                if match.group(2) == "set temp":
                    return f"temperature set to {int(match.group(3))} Degrees"
                elif match.group(2) == "set humidity":
                    return f"humidity set to {int(match.group(3))} Percent Air Wetness"
                elif match.group(2) == "set duration":
                    return f"duration set to {int(match.group(3))} Hours"
            except ValueError:
                return f"specified numeric value for {match.group(2)} wasn't specified correctly\nUse Numeric values without any extra Symbols"
                
        else: 
            attempt = r"^(ferment|fermentation)"
            if attempt:
                return "Fermentation Chamber Please type one of these commands: \n*set temp- ?* \n*set temp- ?*\n*set humidity- ?*\n*set duration- ?*\n*turn off*"
            
if __name__=="__main__":
    main()