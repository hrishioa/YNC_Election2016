import csv, re, time, random
from itertools import permutations
#import msvcrt
from math import factorial
from pyevolve.GenomeBase import GenomeBase

votefile = "votes.csv"
ext_votefile = "avd.csv"
candidates = 14
parse_template = "([\s\S]*?)=>([\s\S]*?)"

def loadvotes():
	votedata = []
	with open(votefile, 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			votedata.append(row[5])
	return votedata[1:len(votedata)]

def get_candidates():
	candidates = []
	with open(ext_votefile, 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			for i in xrange(1, len(row)-1):
				candidates.append(row[i])
			break
	return candidates


def add_external_votes(candidatevotes):
	with open(ext_votefile, 'r') as file:
		reader = csv.reader(file)
		first = True
		for row in reader:
			if first == True:
				first = False
			else:
				for i in xrange(1, len(row)-1):
					candidatevotes[i-1].append(parseEntry(row[i]))
	return candidatevotes
	
def get_parse_object():
	if(get_parse_object.po != None):
		return get_parse_object.po 
	restr = r''
	for x in xrange(0,candidates-1):
		restr+=parse_template+","
	restr+=parse_template+"$"	
	get_parse_object.po = re.compile(restr)
	return get_parse_object.po

get_parse_object.po = None

def print_perm(perm):
	candidate_names = get_candidates()
	for i in xrange(0, len(perm)):
		print "Option %d: Candidate %s" % (len(perm)-i,candidate_names[perm[i]])

def permtoString(perm):
	pstr = ""
	for p in perm:
		pstr+="-"+str(p)
	return pstr

def parseEntry(entry):
	try:
		return int(entry)
	except ValueError as _:
		return -1

def parsevotes(vote):
	match = get_parse_object().match(vote)
	return match.groups(0)

def collate_votes(votedata):
	votes = [parsevotes(vote) for vote in votedata]
	candidatevotes = [[] for x in xrange(0, candidates)]
	for v in xrange(0, len(votes)):
		for i in xrange(0,len(votes[v])):
			if(i%2==0):
				candidatevotes[i/2].append(parseEntry(votes[v][i+1]))
	return candidatevotes

def get_preferences(candidatevotes):
	preferences = []

	for i in xrange(0, len(candidatevotes)):
		for j in xrange(i+1, len(candidatevotes)):
			preferences.append([min(i,j),max(i,j),0,0,0])
	return preferences

def set_preferences(candidatevotes, pref_table):
	for v in xrange(0,len(candidatevotes[0])):
		for cur in xrange(0, len(pref_table)):
			if (candidatevotes[pref_table[cur][0]][v] < candidatevotes[pref_table[cur][1]][v]):
				pref_table[cur][2]+=1
			elif (candidatevotes[pref_table[cur][0]][v] == candidatevotes[pref_table[cur][1]][v]):  
				pref_table[cur][3]+=1
			elif (candidatevotes[pref_table[cur][0]][v] > candidatevotes[pref_table[cur][1]][v]):
				pref_table[cur][4]+=1
	return pref_table

def compare_rankings(rank1, rank2):
	if (max(max(rank1[2],rank1[3]),rank1[4]) < max(max(rank2[2],rank2[3]),rank2[4])):
		return 1
	elif (max(max(rank1[2],rank1[3]),rank1[4]) > max(max(rank2[2],rank2[3]),rank2[4])):
		return -1
	else:
		return 0

def get_perm_score(perm, pref_table):
	pscore = 0
	for i in xrange(0, len(perm)):
		for j in xrange(i+1, len(perm)):
			for p in pref_table:
				if(p[0]==perm[i] and p[1]==perm[j]):
					pscore += p[2]
					break
				elif(p[0]==perm[j] and p[1]==perm[i]):
					pscore += p[4]
					break
	return pscore

def get_time():
	return long(time.time())

def timestr(millis):
	m, s = divmod(millis, 60)
	h, m = divmod(m, 60)
	return ("%d:%02d:%02d" % (h, m, s))

cand = [i for i in xrange(0, candidates)]

def new_perm():
	newp = cand[:]
	random.shuffle(newp)
	assert newp != None
	return newp

def fitness(perm, pref_table):
	return (get_perm_score(perm, pref_table))

def mutate_perm(perm):
	mutatePoint1 = random.randint(0, candidates-1)
	mutatePoint2 = random.randint(0, candidates-1)
	newp = perm[:]
	tmp = newp[mutatePoint1]
	newp[mutatePoint1] = newp[mutatePoint2]
	newp[mutatePoint2] = tmp
	assert newp != None
	return newp

def crossover(perm1, perm2):
	child = [-1 for i in xrange(0, candidates)]
	crossoverPoint = random.randint(0, candidates-1)
	for i in xrange(0, candidates):
		if i < crossoverPoint:
			if not(perm1[i] in child):
				child[i] = perm1[i]
		else:
			if not(perm2[i] in child):
				child[i] = perm2[i]
	for i in xrange(0, candidates):
		if child[i] == -1:
			for j in xrange(0, candidates):
				if not (j in child):
					child[i] = j
	return child

def compare_perm(perm1, perm2):
	ps1 = fitness(perm1, compare_perm.pt)
	ps2 = fitness(perm2, compare_perm.pt)

	if ps1 < ps2:
		return 1
	elif ps1 > ps2:
		return -1
	else:
		return 0

#Begin Execution - no main function so interpreter can retain state
print "System running...\n"
data = collate_votes(loadvotes()) 
data = add_external_votes(data)

pref_table = get_preferences(data)
pref_table = (set_preferences(data, pref_table))

for pref in pref_table:
	assert (pref[2]+pref[3]+pref[4]==len(data[0]))

sorted_prefs = sorted(pref_table, cmp=compare_rankings)

gen_size = 300
rate_mutation = .4
rate_crossover= .2
rate_new = .3
no_generations = 2000

pop = [new_perm() for i in xrange(0, gen_size)]

compare_perm.pt = pref_table

bests = []

start_time = get_time()

for i in xrange(0, no_generations-1):
	newpop = []
	for pick in xrange(0, int(rate_mutation*len(pop))):
		pos = random.randint(0,len(pop)-1)
		newpop.append(mutate_perm(pop[pos]))
	for pick in xrange(0, int(rate_crossover*len(pop))):
		pos1 = random.randint(0,len(pop)-1)
		pos2 = random.randint(0,len(pop)-1)
		newpop.append(crossover(pop[pos1],pop[pos2]))
	for pick in xrange(0, int(rate_new*len(pop))):
		newpop.append(new_perm())
	pop = sorted(pop, cmp=compare_perm)
	for j in xrange(0, int(len(pop)*(1-(rate_new+rate_crossover+rate_mutation)))):
		newpop.append(pop[j][:])
	pop = sorted(newpop, cmp=compare_perm )
	curtime = get_time() - start_time
	if(i>0):
		print "Generation %d ..." % (i)
		print "Best Ranking: "
		print_perm(pop[0])
		print "Best score in population size %d - %d, worst - %d" % (len(pop), fitness(pop[0], pref_table), fitness(newpop[len(pop)-1], pref_table))
		print "Time elapsed: %s, Seconds per generation: %f, Estimated Time remaining: %s" % (timestr(curtime), curtime/i, timestr((float(curtime)/i)*(no_generations-i)))

	bests.append(pop[0])

print "Best score so far - "

print best[len(bests)-1]