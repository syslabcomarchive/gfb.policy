# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.protect.utils import addTokenToUrl


def logit(*kwargs):
    " log something from the web "
    try:
        mesg = ''
        for kwarg in kwargs:
            mesg += str(kwarg) + ' '
        print mesg
    except:
        print [kwargs]


def handle_checkin(obj, event):
    host = getToolByName(obj, 'MailHost')

    portal = getToolByName(obj, 'portal_url').getPortalObject()

    send_from_address = portal.getProperty('email_from_address')
    send_to_address = portal.portal_properties.site_properties.getProperty(
        'external_editor_address', send_from_address)

    rt = getToolByName(obj, "portal_repository", None)
    history = rt.getHistoryMetadata(event.baseline)
    num = int(history.getLength(countPurged=False))
    if num > 0:
        num = num - 1

    obj_url = event.baseline.absolute_url()
    subject = "GFB: Artikel mit Änderungen wurde veröffentlicht"
    history_url = u"{0}/@@history?one=current&two={1}".format(
        safe_unicode(obj_url), num)
    history_url = addTokenToUrl(history_url)

    message = (
        u'Der Artikel "%(title)s" wurde neu veröffentlicht, mit folgendem '
        u'Kommentar:\n%(comment)s\n\nDie Adresse lautet:\n%(url)s.\nHier '
        u'können Sie sich die Änderungen anzeigen lassen:\n%(history)s' % dict(
            title=safe_unicode(obj.Title()),
            history=history_url,
            comment=safe_unicode(event.message),
            url=safe_unicode(obj_url)))

    encoding = portal.getProperty('email_charset')
    msg_type = 'text/plain'

    envelope_from = send_from_address

    host.send(
        message, mto=send_to_address, mfrom=envelope_from,
        subject=subject, msg_type=msg_type, charset=encoding
    )
