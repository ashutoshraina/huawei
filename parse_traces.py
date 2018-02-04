import csv, sys, json, re
from graphviz import Digraph


traceid_fld = 1
spanid_fld = 3
parentid_fld = 8

trace_file = '1st_half_jan_26'

class Span(object):
    def __init__(self, id, parent, data):
        self.id = id
        if parent == "":
            self.parent = 0
        else:
            try:
                self.parent = parent
            except Exception:
                print "BAD value for parentid: " + parent
                self.parent = -1
        self.data = data

class Trace(object):
    def __init__(self, id):
        self.id = id
        self.spans = {}

    def new_span(self, span):
        if span.parent == 0:
            self.root = span
        self.spans[span.id] = span

    def span_cnt(self):
        return len(self.spans.keys())

    def sanity(self):
        has_root = False
        for spanid in self.spans:
            if self.spans[spanid].parent != 0:
                parent = self.spans[spanid].parent
                if parent not in self.spans.keys():
                    print "orphaned id *" + str(parent) + "*"
                    print "with other ids " + str(self.spans.keys())
                    return False
            else:
                has_root = True

        return has_root

    def root_annotations(self):
        return self.root.data

    def get_servicename(self, data):
        p = re.compile("service_name: '(\S+)',")
        m = p.search(data[5])
        if m is not None:
            return m.group(1)
        else:
            p = re.compile("serviceType;(\S+)")
            m = p.search(data[4])
            if m is not None:
                return m.group(1)     
            else:
                return "?"

        

    def to_dot(self):
        g = Digraph(comment="Callgraph", format = "pdf")
        for n in self.spans.values():
            notes = n.data[4]
            g.node(str(n.id), self.get_servicename(n.data))

        for n in self.spans.values():
            g.edge(str(n.parent), str(n.id))
            
        return g


class ZipkinParser(object):
    def __init__(self, file):
        self.big_dict = {}
        with open(file, 'r') as csvfile:
            for trace_entry in csv.reader(csvfile):
                traceid = trace_entry[traceid_fld]
                spanid = trace_entry[spanid_fld]
                parentid = trace_entry[parentid_fld]
                if not traceid in self.big_dict:
                    self.big_dict[traceid] = Trace(traceid)

                trace = self.big_dict[traceid]
                span = Span(spanid, parentid, trace_entry)
                trace.new_span(span)

    def traces(self):
        # probably want an iterator here, but not sure how to do that pythonically.
        return self.big_dict.values()                   
                    

      
parser = ZipkinParser(trace_file)
 
goods = 0
rejects = 0

for trace in parser.traces():
    if trace.sanity():
        goods += 1
        print "ROOT ANNOTATION: " + str(trace.root_annotations())
        dot = trace.to_dot()
        dot.render(trace.id)
    else:
        rejects += 1

