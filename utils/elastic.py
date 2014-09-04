# brew install ElasticSearch
# ensure you've installed a JDK
# launchctl load ~/Library/LaunchAgents/homebrew.mxcl.elasticsearch.plist
# launchctl unload ~/Library/LaunchAgents/homebrew.mxcl.elasticsearch.plist
# install ElasticSearch Head
# plugin -install mobz/elasticsearch-head
# available at http://localhost:9200/_plugin/head/

from pyelasticsearch import ElasticSearch
es = ElasticSearch('http://localhost:9200/')

res = db.session.query(Sign).all()
for r in res:
    d = r.__dict__
    d.pop('_sa_instance_state', None)

# bulk-index the cleaned results
es.bulk_index('cdpp', 'sign', [r.__dict__ for r in res], id_field='id')

# construct a fuzzy search query over the signs
q = {
    "query": {
        "fuzzy_like_this_field" : {
            "sign.sign_ref" : {
                "like_text" : "GESU",
                "max_query_terms" : 10
            }
        },
    }
}
es.search(q, index='cdpp')
