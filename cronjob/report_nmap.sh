echo "Running nmap scan..."

# Report which IPs are visible.
pattern="[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"
for word in $(nmap -sP $RANGE)
do
    [[ $word =~ $pattern ]]
    if [[ ${BASH_REMATCH[0]} ]]
    then
        echo $word
    fi
done

# Report hostnames for IPs, if provided.
# TODO: This is a bit tougher, as this pattern is split over two space-separated words.