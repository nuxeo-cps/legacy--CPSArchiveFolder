## Script (Python) "archivefolder_edit"
##parameters=REQUEST=None, **kw
# $Id$
"""Edit a request folder."""

from zLOG import LOG, DEBUG 

if REQUEST is not None:
    kw.update(REQUEST.form)

doc = context
doc.edit(**kw)

context.portal_eventservice.notifyEvent('modify_object', doc, {})

psm = 'Content+changed'

if REQUEST is not None:
    action_path = 'archivefolder_view'
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
return psm
