import semantic_ndfAPI
import json
import sys

import signal

def signal_handler(sig, frame):
    global was
    with open("was_values.txt", "w") as file:
        for (i, tf) in enumerate(was):
            file.write('{first}: {second}\n'.format(first=i, second = tf))
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Group:
    def __init__(self, y, z):
        self.nGrams = y
        self.sents = z


def intersect(sent1, sent2):
    global dictionary
    result = []
    for s1 in sent1:
        for s2 in sent2:
            if dictionary.isSemanticallyClose(s1, s2):
                result.append(s1)
                break
    return result

def unite(sent1, sent2):
    global dictionary
    return semantic_ndfAPI.Sentence(dictionary, sent1.startIndex, sent2.endIndex, sent1.sent + " " + sent2.sent, sent1.start, sent2.end)


def add_sent(group, sentence, use, idx):
    use[idx] = True
    group.nGrams += sentence.nGrams
    group.sents.append(sentence)


def get_overlap(group, sentence):
    cur_intersect = intersect(sentence.nGrams, group.nGrams)
    cur_overlap = len(cur_intersect) / len(sentence.nGrams)
    return cur_overlap


def set_bool(group, val, use):
    for sentence in group.sents:
        set_sent_bool(sentence, val, use)


def set_sent_bool(sentence, val, use):
    for k in range(sentence.startIndex, sentence.endIndex + 1):
        use[k] = val


name = sys.argv[1]
dictName = sys.argv[2]

if len(sys.argv) >= 4:  # language present
    semantic_ndfAPI.language = sys.argv[3].lower()

with open(dictName, mode = 'rb') as file:
    global dictionary
    dictionary = semantic_ndfAPI.Dictionary(file)

text = semantic_ndfAPI.Text(dictionary, name)
sents = text.sents
classes = []
was = [False for i in range(len(sents))]

for (i, curSent) in enumerate(sents):
    print("i now is: " + str(i) + " out of " + str(len(sents)))
    if not was[i]:
        was[i] = True

        curClass = Group([], [])

        for j in range(i, len(sents)):
            newSent = sents[j]
            if len(newSent.nGrams) == 0:
                continue

            if len(curClass.nGrams) == 0 or get_overlap(curClass, newSent) > 0.5:
                add_sent(curClass, newSent, was, j)

        while len(curClass.sents) > 1:
            newClass = Group([], [])

            for sent in curClass.sents:
                index = sent.endIndex + 1
                if not (index == len(sents) or was[index]):
                    newSent = unite(sent, sents[index])

                    if len(newClass.nGrams) == 0 or get_overlap(newClass, newSent) > 0.5:
                        add_sent(newClass, newSent, was, index)
                        continue

                set_sent_bool(sent, False, was)

            if len(newClass.sents) < 2:
                set_bool(newClass, False, was)
                break

            curClass = newClass

        classes.append(curClass)
        set_bool(curClass, True, was)

cur = 0
jsonArr = []
with open(name + ".result.txt", "w", encoding=text.encoding) as file:
    for curClass in classes:
        # print("print")
        if len(curClass.sents) < 2:
            continue
        cur += 1
        file.write("========================= CLASS #%d =============================\n" % cur)
        file.write('\n'.join(
            ["(%d) <%d> {%d} [%d]: %s" % (sent.startIndex, sent.endIndex, sent.start, sent.end, sent.sent) for sent in
             curClass.sents]))
        file.write("\n*****************************************************************\n")

        curJson = {'group_id': cur}
        ar = []
        for sent in curClass.sents:
            data = {'start_index': sent.start, 'end_index': sent.end, 'text': sent.sent}
            ar.append(data)
        curJson['duplicates'] = ar

        jsonArr.append(curJson)

jsonRes = {'groups': jsonArr}
js = json.dumps(jsonRes, ensure_ascii=False)

with open(name + ".groups.json", "w", encoding=text.encoding) as file:
    file.write(js)
