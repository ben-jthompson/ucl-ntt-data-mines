# dictionary mapping model workflows with the messages to show on the frontend
MESSAGE_DICT = {
    'region': ['Finding regional authorities...', 2],
    'mining': ['Analysing mining environment...', 3],
    'cooling': ['Calculating cooling prospects...', 4],
    'environmental': ['Calculating environmental risk...', 5],
    'data_bibliography': ['Saving data sources...', 6],
    'data_end': ['Searching web for information...', 7],
    'Local Institutions and Expertise': ['Researching local institutions...', 8],
    'Energy Availability': ['Researching local energy infrastructure...', 9],
    'Local Authorities': ['Researching local authorities...', 10],
    'Local Mine Reclamation Projects': ['Researching local mining projects...', 11],
    'Transport Infrastructure': ['Researching local transport...', 12],
    'pdf_creation': ['Creating your report...', 13],
    'metadata': ['Creating your file...', 14],
    'zipper': ['Zipping your documents...', 15],
    'done': ['Done! Click next to see your new report.', 16]
}

QUERY_DICT = [
    {'tag': 'Labour Availability', 'topic': 'Local Institutions and Expertise', 'search_query': 'Universities or mining-based expertise near or', 'plain_query': "What universities or mining-based expertise are nearby, ", 'example':'The nearby universities with mining expertise in Bestwood Village, Gedling, UK, include the University of Nottingham, which is ranked 2nd in the UK for Mineral and Mining Engineering, Nottingham Trent University, and the University of Sheffield. These institutions offer various programs and research opportunities related to mining and engineering. Proximity to relevant institutions is important to source experts to guide aspects such as planning and maintenance when implementing data centres within coal mines.'},
    {'tag': 'Energy Availability', 'topic': 'Energy Availability', 'search_query': 'Renewable energy availability and power plants near or', 'plain_query': "What power plants and renewable energy projects are nearby, "},
    {'tag': 'Local Authorities', 'topic': 'Local Authorities', 'search_query': 'Local authorities and councils mining support near or', 'plain_query': "How are local authorities and councils supporting mining regeneration and reuse, "},
    {'tag': 'Existing Mine Projects', 'topic': 'Local Mine Reclamation Projects', 'search_query': 'Mine reuse projects near or', 'plain_query': "What mine reuse/regeneration projects are nearby, "},
    {'tag': 'Transport Availability', 'topic': 'Transport Infrastructure', 'search_query': 'Transport links to/near or', 'plain_query': "What transport links are nearby, "},
]