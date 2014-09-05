# brew install ElasticSearch
# ensure you've installed a JDK
# launchctl load ~/Library/LaunchAgents/homebrew.mxcl.elasticsearch.plist
# launchctl unload ~/Library/LaunchAgents/homebrew.mxcl.elasticsearch.plist
# install ElasticSearch Head
# plugin -install mobz/elasticsearch-head
# available at http://localhost:9200/_plugin/head/

from pyelasticsearch import ElasticSearch
es = ElasticSearch('http://localhost:9200/')
es.delete_index('cdpp')
res = db.session.query(Sign).all()
for r in res:
    d = r.__dict__
    d.pop('_sa_instance_state', None)
# bulk-index the cleaned signs
es.bulk_index('cdpp', 'sign', [r.__dict__ for r in res], id_field='id')



tablets = db.session.query(Tablet).all()
repr = []
for result in tablets:
    d = result.__dict__
    keys = ['medium', 'city', 'period', 'sub_period', 'text_vehicle', 'method', 'genre', 'museum_number']
    as_dict = {}
    for key in keys:
        value = getattr(result, key)
        if value:
            as_dict[key] = unicode(value)
    if result.rulers:
        as_dict['ruler'] = result.rulers[0].name
    as_dict['id'] = result.id
    repr.append(as_dict)
# bulk-index the cleaned tablets
es.bulk_index('cdpp', 'tablet', repr, id_field='id')

# TODO BULK-INDEXING CAN CAUSE DUPLICATE IDS FIX THIS NOW
