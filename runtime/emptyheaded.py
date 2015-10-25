import json
import codegenerator.createDB
import codegenerator.env
import codegenerator.fetchRelation
import subprocess
import codegenerator.cppgenerator as cppgenerator
import codegenerator.cppexecutor as cppexecutor
import os

environment = codegenerator.env.Environment()

def query(datalog_string):
  qcpath = os.path.expandvars("$EMPTYHEADED_HOME")+"/query_compiler/"
  os.chdir(qcpath)
  subprocess.Popen("target/start -c %s/config.json \"%s\"" % (environment.config["database"],datalog_string), cwd='../query_compiler' ,shell=True, stdout=subprocess.PIPE).stdout.read()
  environment.fromJSON(environment.config["database"]+"/config.json")
  cppgenerator.compileC("Query")
  schema = environment.schemas[environment.config["resultName"]]
  eTypes = map(lambda i:str(schema["attributes"][i]["attrType"]),environment.config["resultOrdering"])
  result = cppexecutor.execute("Query",environment.config["memory"],eTypes,schema["annotation"])
  environment.liverelations[environment.config["resultName"]] = result

def compileQuery(datalog_string):
  print subprocess.Popen("target/start DunceCap.QueryPlanner %s \"%s\"" % (QUERY_COMPILER_CONFIG_DIR, datalog_string), cwd='../query_compiler' ,shell=True, stdout=subprocess.PIPE).stdout.read()

def createDB(name):
  name = os.path.expandvars(name)
  codegenerator.createDB.fromJSON(name,environment)
  #environment.dump()

def fetchData(relation):
	if relation in environment.liverelations:
		return environment.liverelations[relation][0].fetch_data(environment.liverelations[relation][1])
	else:
  		return codegenerator.fetchRelation.fetch(relation,environment)

def numRows(relation):
	if relation in environment.liverelations:
		return environment.liverelations[relation][0].num_rows(environment.liverelations[relation][1])
	else:
  		return codegenerator.fetchRelation.numRows(relation,environment)

def saveDB():
  environment.toJSON(environment.config["database"]+"/config.json")

def loadDB(path):
  path = os.path.expandvars(path)+"/config.json"
  environment.fromJSON(path)

def main():
	db_config="$EMPTYHEADED_HOME/examples/graph/data/facebook/config_pruned.json"
	createDB(db_config)
	loadDB("$EMPTYHEADED_HOME/examples/graph/data/facebook/db_pruned")
	query("Triangle(a,b,c) :- Edge(a,b),Edge(b,c),Edge(a,c).")

	print numRows("Triangle")
	print fetchData("Triangle")[0]

if __name__ == "__main__": main()
