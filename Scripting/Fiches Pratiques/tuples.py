equipement = ("SW-CORE-01", "192.168.10.1", "switch")
print (equipement)

print ("Nom :", equipement[0])
print ("IP :", equipement[1])
print ("Type :", equipement[2])



equipement_liste = ["SW-CORE-01", "192.168.10.1", "switch"]
equipement_liste[1] = "192.168.10.2"
print (equipement_liste)

for info in equipement:
    print(info)
