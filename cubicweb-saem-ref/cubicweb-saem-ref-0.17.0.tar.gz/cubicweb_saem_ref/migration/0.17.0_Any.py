for etype in ('Agent', 'OrganizationUnit'):
    wf = get_workflow_for(etype)
    wf.transition_by_name('publish').cw_delete()
    wf.state_by_name('draft').cw_delete()
    wf.cw_set(initial_state=wf.state_by_name('published'))
    cnx.execute('DELETE TrInfo X WHERE NOT X from_state S')
    cnx.commit()
