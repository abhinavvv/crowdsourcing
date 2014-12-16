import pickle
import gzip
import math
from collections import OrderedDict

# Load stuff

with open('a.pik', 'rb') as pk:
    a = pickle.load(pk)

with open('rank_topic_cosine', 'rb') as pk:
    rank_topic_cosine = pickle.load(pk)

with open('rank_bow_cosine', 'rb') as pk:
    rank_bow_cosine = pickle.load(pk)

with open('rank_wdiff', 'rb') as pk:
    rank_wdiff = pickle.load(pk)

with open('rank_topic_euclidean', 'rb') as pk:
    rank_topic_euclidean = pickle.load(pk)


diff_users = {}


def compute_diff_user(rank_topic, rank_word):
    for user, rank in rank_topic.iteritems():
        val = math.fabs(float(1)/rank - float(1)/rank_word[user])
        diff_users[user] = val


compute_diff_user(rank_topic_cosine, rank_wdiff)

diff_users = OrderedDict(sorted(diff_users.items(), key=lambda x: -x[1]))
print 'Total users: ', len(set(a))
print 'Length of diff_users: ', len(diff_users)

for user, val in diff_users.iteritems():
    print user + '  Value: ' + str(val) + '  Rank by topic distance: ' + str(rank_topic_euclidean[user]) \
        + '  Rank by edit distance: '+ str(rank_wdiff[user])