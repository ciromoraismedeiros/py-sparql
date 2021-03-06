import rdflib, os
from flask import Flask, render_template, request, escape

app = Flask(__name__)

def shorten_iri(iri, namespaces):
    r = str(iri)
    shortened=False
    for pref, uri in namespaces:
        if r.startswith(uri):
            r = str(escape(r.replace(uri,pref+':')))
            break    
    if len(r)>30:
        r = r[:11]+'...'+r[-15:]
    return r

@app.route('/', methods=['GET','POST'])
def home():
    filenames = os.listdir('data') # list of files in data directory
    last = ''   # last data file chosen
    query_text = 'SELECT ?s ?p ?o\nWHERE {\n    ?s ?p ?o\n}\nLIMIT 100'
    ans = []    # answers for SELECT queries
    tps = []    # triples for CONSTRUCT queries
    vrbs = None # query's selected variables
    
    if request.method == 'POST':
        g = rdflib.Graph()
        last = request.form['file']
        query_text = request.form['query']
        f = 'data/'+last
        g.parse(f, format=rdflib.util.guess_format(f))
        tupl = None
        q = g.query(query_text)
        
        if q.type == 'SELECT':
            vrbs = q.vars
            for row in q:
                row = row.asdict()
                a = []
                for k in vrbs:
                    k = str(k)
                    v = shorten_iri(row[k],g.namespaces()) if k in row else 'null'
                    a += [v]
                ans += [a]
            
        
        elif q.type == 'CONSTRUCT':
            #q.save('data/q.ttl', format='turtle')
            for t in q:
                t = tuple([shorten_iri(x, g.namespaces()) for x in t])
                tps += [t]

    return render_template('home.html', answers=ans, last=last,
        filenames=filenames, query_text=query_text, 
        variables=vrbs, triples=tps)


