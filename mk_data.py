
import requests
import json
import re
import random
import argparse

# Byte limit for bulk request bodies
BULK_REQ_LIMIT = 1e6

def resp(r):
    print(r.status_code)
    print(json.dumps(json.loads(r.content), indent=4))
    return r

def _insert(url, body, n, index):
    print("Inserting %d entries into index %s" % (n, index), flush=True)

    requests.post(url + "/_bulk", data=body, headers={
        "Content-Type": "application/json",
    }).raise_for_status()

    print("Inserted %d entries into index %s" % (n, index), flush=True)

def bulk_insert(url, data, index="test"):
    _iter = iter(data)
    done = False

    while not done:
        body = ""
        l = 0
        i = 0

        while True:
            try:
                x = next(_iter)
            except StopIteration:
                done = True
                break

            encoded = ('%s\n%s\n' % (
                json.dumps({
                    "index": {
                        "_index": index,
                        "_type": "_doc"
                    }
                }),
                json.dumps(x)
            ))

            if i % 5000 == 0:
                _chars = ['/', '-', '\\', '|']
                print("%c\b" % _chars[int(i / 5000) % len(_chars)], end="")

            if len(x) + l >= BULK_REQ_LIMIT:
                _insert(url, body, i, index)
                body = ""
                l = 0
                i = 0

            body += encoded
            l += len(encoded)
            i += 1
        
        if len(body) > 0:
            _insert(url, body, i, index)

def get_words():
    with open("junk_text", "r") as infile:
        return sorted(set(re.split("\\s+", infile.read().replace(".", ""))))

def create_sentences(words, n, min_words=5, max_words=20):
    for i in range(n):
        sentence = []
        for _i in range(random.randint(min_words, max_words)):
            sentence.append(random.choice(words))
        yield {"test": " ".join(sentence)}

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elastic-host", dest="url", required=True)
    parser.add_argument("--index", dest="index", default="test")
    parser.add_argument("-n", "--count", dest="count", default=1000, type=int)

    args = parser.parse_args()

    print("Deleting index %s..." % args.index)
    resp(requests.delete(args.url + "/" + args.index, headers={"Content-Type": "application/json"}))
    print("Deleted index %s" % args.index)

    print("Creating index %s" % args.index)
    resp(requests.put(args.url + "/" + args.index, json={
        "mappings": {
            "_doc": {
                "properties": {
                    "test": {
                        "type": "text", # enables full text search
                        "fielddata": True,
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
        },
        "blocks": {
            "read_only_delete": False
        }
    })).raise_for_status()
    print("Created index %s" % args.index)

    if args.count > 0:
        bulk_insert(args.url, create_sentences(get_words(), args.count), args.index)

if __name__ == "__main__":
    run()
