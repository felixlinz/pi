import re

def main():
    print(processingـincomingـmessages(input("Message: ")))
    

def processingـincomingـmessages(text):
        match = re.search(r"^(ferment)\b.*\b(set \w*)\b.*\-\s*(\d*)", text)
        if match:
            print(match.group(1))
            print(match.group(2))
            print(match.group(3))
            if match.group(2) == "set temp":
                return f"temperature set to {match.group(3)} Degrees"
        else: 
            return 'incorrect input'
            
if __name__=="__main__":
    main()