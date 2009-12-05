"""
python wrapper for accessing the SmugMug API

Smugapi is a python wrapper for acessing the SmugMug API.  It allows you to
manipulate Categories, SubCategories, Albums, and Images, all in a
very object-oriented way.
"""

#
# Copyright 2009, Chris Lalancette
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import xmlrpclib
import os
import simplejson
import urllib
import pycurl
import cStringIO

_jsonurl_ = "https://api.smugmug.com/services/api/json/1.2.0/"
_xmlrpcurl_ = "https://api.smugmug.com/services/api/xmlrpc/1.2.0/"

class SmugException(Exception):
    """
    A customized exception class, so you can do:

    try:
         code
    except SmugException:
         do_something

    while still seeing other exceptions.
    """
    pass

class SmugImage:
    """
    This class represents an Image in SmugMug.  Note that this class should
    never be instantiated directly; instead, the SmugAlbum list image
    method should be used, which will properly instantiate objects of
    this type.
    """
    def __init__(self, sp, session, metadata):
        self.sp = sp
        self.session = session
        self.metadata = metadata

    def __str__(self):
        return "%d:\t%s" % (self.get_id(), self.get_filename())

    def get_id(self):
        """
        Get the image ID attribute.  This is the main identifier for this
        image, and is unique across all images in your profile. This is a
        read-only attribute.
        """
        return self.metadata['id']
    def get_key(self):
        """
        Get the image Key attribute. This is a read-only attribute.
        """
        return self.metadata['Key']

    def _json_call_(self, method, field, value):
        # FIXME: does smugmug.images.changeSettings work via XML-RPC?
        #self.sp.smugmug.images.changeSettings(self.session, self.id, newtitle)
        call = "%s?method=smugmug.images.%s&SessionID=%s&ImageID=%d&%s=%s" % (_jsonurl_, method, self.session, self.get_id(), field, value)
        call = urllib.quote(call, safe="%/:=&?~#+!$,;'@()*[]")
        change = simplejson.loads(urllib.urlopen(call).read())
        if change['stat'] == 'fail':
            raise SmugException, "Failed to change title: code %s, message %s" % (change['code'], change['message'])

        # Refresh our data from the server.  It's a bit heavyweight, but this
        # ensures that we are always up-to-date
        for image in self.sp.smugmug.images.get(self.session, self.metadata['Album']['id'], True, self.metadata['Album']['Key'])["Images"]:
            if image['id'] == self.get_id():
                self.metadata = image
                break

    def get_albumid(self):
        """
        Get the AlbumID to which this album belongs.
        """
        return self.metadata['Album']['id']
    def set_albumid(self, newalbumid, newalbumkey):
        """
        Move this image to a different album with albumid 'newalbumid' and
        albumkey 'newalbumkey'.
        """
        if newalbumid == self.get_albumid():
            return
        self._json_call_('changeSettings', 'AlbumID', newalbumid)
        # because we are changing albums here, we actually have to refresh
        # the data from the server here, using the new album
        for image in self.sp.smugmug.images.get(self.session, newalbumid, True, newalbumkey)["Images"]:
            if image['id'] == self.get_id():
                self.metadata = image
                break

    def get_albumkey(self):
        """
        Get the AlbumID to which this album belongs.
        """
        return self.metadata['Album']['Key']

    def get_caption(self):
        """
        Get the image Caption attribute.
        """
        return self.metadata['Caption']
    def set_caption(self, newcaption):
        """
        Set the image Caption (string).
        """
        self._json_call_('changeSettings', 'Caption', newcaption)

    def get_keywords(self):
        """
        Get the image Keywords attribute.
        """
        if len(self.metadata['Keywords']) == 0:
            return []
        return self.metadata['Keywords'].split(',')
    def set_keywords(self, newkeywords):
        """
        Set the image Keywords attribute (list).
        """
        if not isinstance(newkeywords, list):
            raise SmugException, "The Keywords parameter must be a list"
        if newkeywords == self.get_keywords():
            return
        self._json_call_('changeSettings', 'Keywords', ', '.join(newkeywords))

    def get_hidden(self):
        """
        Get the image Hidden attribute.  This attribute describes whether
        this image can be seen by the public or not.  By default, images
        are created publically.
        """
        return self.metadata['Hidden']
    def set_hidden(self, newhidden):
        """
        Set the image Hidden attribute (bool).
        """
        if not isinstance(newhidden, bool):
            raise SmugException, "The Hidden property must be 'True' or 'False'"
        self._json_call_('changeSettings', 'Hidden', int(newhidden))

    def get_position(self):
        """
        Get the image position in the album.
        """
        return self.metadata['Position']
    def set_position(self, newposition):
        """
        Set the image position in the album.
        """
        self._json_call_('changePosition', 'Position', newposition)

    def get_filename(self):
        """
        Get the image FileName attribute (read-only).
        """
        return self.metadata['FileName']

    def get_date(self):
        """
        Get the image Date attribute (read-only).
        """
        return self.metadata['Date']

    def get_format(self):
        """
        Get the image Format attribute (read-only).
        """
        return self.metadata['Format']

    def get_serial(self):
        """
        Get the image Serial attribute (read-only).
        """
        return self.metadata['Serial']

    def get_size(self):
        """
        Get the image Size attribute (read-only).
        """
        return self.metadata['Size']

    def get_width(self):
        """
        Get the image Width attribute (read-only).
        """
        return self.metadata['Width']

    def get_height(self):
        """
        Get the image Height attribute (read-only).
        """
        return self.metadata['Height']

    def get_md5sum(self):
        """
        Get the image MD5Sum attribute (read-only).
        """
        return self.metadata['MD5Sum']

    def get_lastupdated(self):
        """
        Get the image LastUpdated attribute (read-only).
        """
        return self.metadata['LastUpdated']

    def get_albumurl(self):
        """
        Get the image AlbumURL attribute (read-only).
        """
        return self.metadata['AlbumURL']

    def get_tinyurl(self):
        """
        Get the image TinyURL attribute (read-only).
        """
        return self.metadata['TinyURL']

    def get_thumburl(self):
        """
        Get the image ThumbURL attribute (read-only).
        """
        return self.metadata['ThumbURL']

    def get_smallurl(self):
        """
        Get the image SmallURL attribute (read-only).
        """
        return self.metadata['SmallURL']

    def get_mediumurl(self):
        """
        Get the image MediumURL attribute (read-only).
        """
        return self.metadata['MediumURL']

    def get_largeurl(self):
        """
        Get the image LargeURL attribute (read-only).
        """
        return self.metadata['LargeURL']

    def get_xlargeurl(self):
        """
        Get the image XLargeURL attribute (read-only).
        """
        return self.metadata['XLargeURL']

    def get_x2largeurl(self):
        """
        Get the image X2LargeURL attribute (read-only).
        """
        return self.metadata['X2LargeURL']

    def get_x3largeurl(self):
        """
        Get the image X3LargeURL attribute (read-only).
        """
        return self.metadata['X3LargeURL']

    def get_originalurl(self):
        """
        Get the image OriginalURL attribute (read-only).
        """
        return self.metadata['OriginalURL']

    def get_latitude(self):
        """
        Get the image Latitude attribute (read-only).
        """
        return self.metadata['Latitude']

    def get_longitude(self):
        """
        Get the image Longitude attribute (read-only).
        """
        return self.metadata['Longitude']

    def get_altitude(self):
        """
        Get the image Altitude attribute (read-only).
        """
        return self.metadata['Altitude']

    def get_exif(self):
        """
        Get the image EXIF data (read-only).
        """
        return self.sp.smugmug.images.getEXIF(self.session, self.get_id(), self.get_key())['Image']

    def get_watermark(self):
        """
        Get the image watermark data (read-only).
        """
        return self.metadata['Watermark']

    def download_data(self, callback=None):
        """
        Download the image data.
        """
        def data(buf):
            self.full += buf

        c = pycurl.Curl()
        c.setopt(c.URL, self.get_originalurl())
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 300)
        self.full = ""
        c.setopt(c.WRITEFUNCTION, data)

        if callback is not None:
            c.setopt(c.NOPROGRESS, 0)
            c.setopt(c.PROGRESSFUNCTION, callback)

        c.perform()
        c.close()

        return self.full

    def download_data_to_file(self, filename, callback=None):
        """
        Download the image data to a file.
        """
        f = open(filename, "w")
        f.write(self.download_data(callback))
        f.close()

    def delete(self):
        """
        Delete this image.  Oncee this method has been called, this image
        instance is invalid and should not be used.
        """
        # FIXME: we really should update the data in our parent SmugAlbum
        # after we've done this.  However, I don't have a pointer to it
        # here, so it's not easy to do.
        self.sp.smugmug.images.delete(self.session, self.get_id())

class SmugAlbum:
    """
    This class represents an Album in SmugMug.  Note that this class should
    never be instantiated directly; instead, the SmugMug find album
    method should be used, which will properly instantiate objects
    of this type.
    """
    def __init__(self, sp, session, album):
        self.sp = sp
        self.session = session
        self.album = album

    def __str__(self):
        return "%d:\t%s" % (self.get_id(), self.get_title())

    # Album AlbumID; is not changeable, so no "set_id"
    def get_id(self):
        """
        Get the album ID attribute.  This is the main identifier for this
        album, and is unique across all albums in your profile. This is a
        read-only attribute.
        """
        return self.album['id']

    def _json_call_(self, field, value):
        # FIXME: it seems the XMLRPC changesettings method doesn't actually
        # work (it returns an Internal Server Error), so fall back to JSON
        #self.sp.smugmug.albums.changeSettings(self.session, self.id, newtitle)
        call = "%s?method=smugmug.albums.changeSettings&SessionID=%s&AlbumID=%d&%s=%s" % (_jsonurl_, self.session, self.get_id(), field, value)
        call = urllib.quote(call, safe="%/:=&?~#+!$,;'@()*[]")
        change = simplejson.loads(urllib.urlopen(call).read())
        if change['stat'] == 'fail':
            raise SmugException, "Failed to change title: code %s, message %s" % (change['code'], change['message'])

        # Refresh our data from the server.  It's a bit heavyweight, but this
        # ensures that we are always up-to-date
        albums = self.sp.smugmug.albums.get(self.session, "", True)["Albums"]
        for album in albums:
            if album['id'] == self.get_id():
                self.album = album
                break

    def _set_bool_(self, field, value):
        if not isinstance(value, bool):
            raise SmugException, "The %s property must be 'True' or 'False'" % field
        if value == self.album[field]:
            return
        self._json_call_(field, int(value))

    def _set_string_(self, field, value):
        if value == self.album[field]:
            return
        self._json_call_(field, value)

    def _set_int_(self, field, value):
        if not isinstance(value, int):
            raise SmugException, "The %s property must be an integer, given a %s" % (field, type(value))
        if value == self.album[field]:
            return
        self._json_call_(field, str(value))

    def _get_dict_(self, dict, val, getint=False):
        for key, value in dict.items():
            if val == value:
                if not getint:
                    return key
                else:
                    return value
        return None
    def _set_dict_(self, dict, field, value):
        if not value in dict.keys() + dict.values():
            raise SmugException, "The " + field + " property must be one of " + ', '.join([`num` for num in dict.keys()])
        if value in dict.keys():
            value = dict[value]

        if value == self.album[field]:
            return
        self._json_call_(field, str(value))

    def _set_id_(self, field, value):
        fieldname = field.partition('ID')[0]
        if hasattr(self.album, fieldname) and value == self.album[fieldname]['id']:
            return
        self._json_call_(field, str(value))

    def get_title(self):
        """
        Get the album Title attribute.  This is the main title of the
        album, but note that titles are not unique in SmugMug.
        """
        return self.album['Title']
    def set_title(self, newtitle):
        """
        Set the album Title attribute (string).
        """
        self._set_string_('Title', newtitle)

    # FIXME: we should return category and subcategory objects here

    def get_categoryid(self):
        """
        Get the album CategoryID attribute.  This is the SmugMug Category
        to which this album belongs.  By default, albums are placed into
        the 'Other' Category.
        """
        return self.album['Category']['id']
    def set_categoryid(self, newcategoryid):
        """
        Set the album CategoryID attribute. Note that the Category must
        exist or this will throw an exception.
        """
        self._set_id_('CategoryID', newcategoryid)

    def get_subcategoryid(self):
        """
        Get the album SubCategoryID attribute.  This  is the SmugMug
        SubCategory to which this album belongs.  By default, albums have
        no SubCategory.
        """
        if 'SubCategory' in self.album:
            return self.album['SubCategory']['id']
        else:
            return None
    def set_subcategoryid(self, newsubcategoryid):
        """
        Set the album SubCategoryID attribute.  Note that the SubCategory
        must exist or this will throw an exception.
        """
        self._set_id_('SubCategoryID', newsubcategoryid)

    def get_description(self):
        """
        Get the album Description attribute.  This is the main descriptive
        text on the album.
        """
        return self.album['Description']
    def set_description(self, newdescription):
        """
        Set the album Description attribute (string).
        """
        self._set_string_('Description', newdescription)

    def get_keywords(self):
        """
        Get the album Keywords attribute.
        """
        if len(self.album['Keywords']) == 0:
            return []
        return self.album['Keywords'].split(',')
    def set_keywords(self, newkeywords):
        """
        Set the album Keywords attribute (list).
        """
        if not isinstance(newkeywords, list):
            raise SmugException, "The Keywords parameter must be a list"
        if newkeywords == self.get_keywords():
            return
        self._json_call_('Keywords', ','.join(newkeywords))

    def get_geography(self):
        """
        Get the album Geography attribute.
        """
        return self.album['Geography']
    def set_geography(self, newgeography):
        """
        Set the album Geography attribute (bool).
        """
        self._set_bool_('Geography', newgeography)

    def get_highlightid(self):
        """
        Get the album HighlightID album attribute.
        """
        return self.album['Highlight']['id']
    def set_highlightid(self, newhighlightid):
        """
        Set the album HighlightID attribute.
        """
        self._set_id_('HighlightID', newhighlightid)

    def get_position(self):
        """
        Get the album Position attribute.
        """
        return self.album['Position']
    def set_position(self, newposition):
        """
        Set the album Position attribute (int).
        """
        self._set_int_('Position', newposition)

    # FIXME: skip power setting "Header"

    def get_imagecount(self):
        """
        Get the album ImageCount attribute.  This attribute describes how
        many images are in the album, and is a read-only attribute.
        """
        return self.album['ImageCount']

    def get_key(self):
        """
        Get the album Key attribute. This is a read-only attribute.
        """
        return self.album['Key']

    def get_lastupdated(self):
        """
        Get the album LastUpdated attribute.  This attribute shows the
        last time this album was updated (in YYYY-MM-DD HH:MM:SS US PST),
        and is a read-only attribute.
        """
        return self.album['LastUpdated']

    def get_clean(self):
        """
        Get the album Clean attribute.  This boolean attribute describes
        whether this album is 'clean' from offensive content.
        """
        return self.album['Clean']
    def set_clean(self, newclean):
        """
        Set the album Clean attribute (bool).
        """
        self._set_bool_('Clean', newclean)

    def get_exif(self):
        """
        Get the album EXIF attribute.
        """
        return self.album['EXIF']
    def set_exif(self, newexif):
        """
        Set the album EXIF attribute (bool).
        """
        self._set_bool_('EXIF', newexif)

    def get_filenames(self):
        """
        Get the album Filenames attribute.
        """
        return self.album['Filenames']
    def set_filenames(self, newfilenames):
        """
        Set the album Filenames attribute (bool).
        """
        self._set_bool_('Filenames', newfilenames)

    def get_squarethumbs(self):
        """
        Get the album SquareThumbs attribute.
        """
        return self.album['SquareThumbs']
    def set_squarethumbs(self, newsquarethumbs):
        """
        Set the album SquareThumbs attribute (bool).
        """
        self._set_bool_('SquareThumbs', newsquarethumbs)

    templateids = { "Viewer Choice": 0,
                    "SmugMug": 3,
                    "Traditional": 4,
                    "All Thumbs": 7,
                    "Slideshow": 8,
                    "Journal": 9,
                    "SmugMug Small": 10,
                    "Filmstrip": 11 }
    def get_templateid(self, getint=False):
        """
        Get the album TemplateID attribute.  This attribute controls how
        this album is shown to the user.  The default is 'Viewer Choice'.
        """
        return self._get_dict_(SmugAlbum.templateids, self.album['Template']['id'], getint)
    def set_templateid(self, newtemplateid):
        """
        Set the album TemplateID attribute (one of 'Viewer Choice',
        'SmugMug', 'Traditional', 'All Thumbs', 'Slideshow', 'Journal',
        'SmugMug Small', or 'Filmstrip').
        """
        if not newtemplateid in SmugAlbum.templateids.keys() + SmugAlbum.templateids.values():
            raise SmugException, "The TemplateID property must be one of " + ', '.join([`num` for num in SmugAlbum.templateids.keys()])
        if newtemplateid in SmugAlbum.templateids.keys():
            newtemplateid = SmugAlbum.templateids[newtemplateid]
        self._set_id_('TemplateID', newtemplateid)

    def get_sortmethod(self):
        """
        Get the album SortMethod attribute.  This attribute describes how
        the images in this album are sorted. By default albums are sorted
        by 'Position'.
        """
        return self.album['SortMethod']
    def set_sortmethod(self, newmethod):
        """
        Set the album SortMethod attribute (one of 'Position', 'Caption',
        'FileName', 'Date', 'DateTime', 'DateTimeOriginal').
        """
        methods = ['Position', 'Caption', 'FileName', 'Date', 'DateTime', 'DateTimeOriginal']
        if not newmethod in methods:
            raise SmugException, "Invalid sort method, it must be one of " + ', '.join([`num` for num in methods])
        if newmethod == self.get_sortmethod():
            return
        self._json_call_('SortMethod', newmethod)

    sortdirections = { "Ascending": 0,
                       "Descending": 1 }
    def get_sortdirection(self, getint=False):
        """
        Get the album SortDirection attribute.  By default albums are
        sorted in 'Ascending' order.
        """
        return self._get_dict_(SmugAlbum.sortdirections, self.album['SortDirection'], getint)
    def set_sortdirection(self, newdirection):
        """
        Set the album SortDirection attribute (one of 'Ascending' or
        'Descending').
        """
        self._set_dict_(SmugAlbum.sortdirections, 'SortDirection', newdirection)

    def get_password(self):
        """
        Get the album Password attribute.  This attribute places a
        password on this album.  By default albums have no password.
        """
        return self.album['Password']
    def set_password(self, newpassword):
        """
        Set the album Password attribute (string).
        """
        self._set_string_('Password', newpassword)

    def get_passwordhint(self):
        """
        Get the album PasswordHint attribute.
        """
        return self.album['PasswordHint']
    def set_passwordhint(self, newpasswordhint):
        """
        Set the album PasswordHint attribute (string).
        """
        self._set_string_('PasswordHint', newpasswordhint)

    def get_public(self):
        """
        Get the album Public attribute.  This attribute describes whether
        this album can be seen by the public or not.  By default, albums
        are created publically.
        """
        return self.album['Public']
    def set_public(self, newpublic):
        """
        Set the album Public attribute (bool).
        """
        self._set_bool_('Public', newpublic)

    def get_worldsearchable(self):
        """
        Get the album WorldSearchable attribute.  This attribute describes
        whether this album can be searched from anywhere on the internet.
        By default albums are world searchable.
        """
        return self.album['WorldSearchable']
    def set_worldsearchable(self, newworldsearchable):
        """
        Set the album WorldSearchable attribute (bool).
        """
        self._set_bool_('WorldSearchable', newworldsearchable)

    def get_smugsearchable(self):
        """
        Get the album SmugSearchable attribute.  This attribute describes
        whether this album can be searched from within SmugMug.  By default
        albums are Smug searchable.
        """
        return self.album['SmugSearchable']
    def set_smugsearchable(self, newsmugsearchable):
        """
        Set the album SmugSearchable attribute (bool).
        """
        self._set_bool_('SmugSearchable', newsmugsearchable)

    def get_external(self):
        """
        Get the album External attribute.
        """
        return self.album['External']
    def set_external(self, newexternal):
        """
        Set the album External attribute (bool).
        """
        self._set_bool_('External', newexternal)

    # FIXME: skip power setting "Protected"
    # FIXME: skip power setting "Watermarking"
    # FIXME: skip power setting "WatermarkID"

    def get_hideowner(self):
        """
        Get the album HideOwner attribute.
        """
        return self.album['HideOwner']
    def set_hideowner(self, newhideowner):
        """
        Set the album HideOwner attribute (bool).
        """
        self._set_bool_('HideOwner', newhideowner)

    # FIXME: skip power setting "Larges"
    # FIXME: skip power setting "XLarges"

    def get_x2larges(self):
        """
        Get the album X2Larges attribute.
        """
        return self.album['X2Larges']
    def set_x2larges(self, newx2larges):
        """
        Set the album X2Larges attribute (bool).
        """
        self._set_bool_('X2Larges', newx2larges)

    def get_x3larges(self):
        """
        Get the album X3Larges attribute.
        """
        return self.album['X3Larges']
    def set_x3larges(self, newx3larges):
        """
        Set the album X3Larges attribute (bool).
        """
        self._set_bool_('X3Larges', newx3larges)

    def get_originals(self):
        """
        Get the album Originals attribute.
        """
        return self.album['Originals']
    def set_originals(self, neworiginals):
        """
        Set the album Originals attribute (bool).
        """
        self._set_bool_('Originals', neworiginals)

    def get_canrank(self):
        """
        Get the album CanRank attribute.
        """
        return self.album['CanRank']
    def set_canrank(self, newcanrank):
        """
        Set the album CanRank attribute (bool).
        """
        self._set_bool_('CanRank', newcanrank)

    # Album FriendEdit
    def get_friendedit(self):
        """
        Get the album FriendEdit attribute.
        """
        return self.album['FriendEdit']
    def set_friendedit(self, newfriendedit):
        """
        Set the album FriendEdit attribute (bool).
        """
        self._set_bool_('FriendEdit', newfriendedit)

    def get_familyedit(self):
        """
        Get the album FamilyEdit attribute.
        """
        return self.album['FamilyEdit']
    def set_familyedit(self, newfamilyedit):
        """
        Set the album FamilyEdit attribute (bool).
        """
        self._set_bool_('FamilyEdit', newfamilyedit)

    def get_comments(self):
        """
        Get the album Comments attribute.  This attribute controls whether
        comments are allowed on this album or not.  By default, album
        comments are allowed.
        """
        return self.album['Comments']
    def set_comments(self, newcomments):
        """
        Set the album Comments attribute (bool).
        """
        self._set_bool_('Comments', newcomments)

    def get_share(self):
        """
        Get the album Share attribute.
        """
        return self.album['Share']
    def set_share(self, newshare):
        """
        Set the album Share attribute (bool).
        """
        self._set_bool_('Share', newshare)

    def get_printable(self):
        """
        Get the album Printable attribute.  This attribute controls whether
        the images in this album can be printed or not.  By default, album
        images can be printed.
        """
        return self.album['Printable']
    def set_printable(self, newprintable):
        """
        Set the album Printable attribute (bool).
        """
        self._set_bool_('Printable', newprintable)

    # Album ColorCorrection
    colorcorrections = { "No": 0,
                         "Yes": 1,
                         "Inherit": 2 }
    def get_colorcorrection(self, getint=False):
        """
        Get the album ColorCorrection attribute.
        """
        return self._get_dict_(SmugAlbum.colorcorrections, self.album['ColorCorrection'], getint)
    def set_colorcorrection(self, newcolorcorrection):
        """
        Set the album ColorCorrection attribute (one of 'No', 'Yes', or
        'Inherit').
        """
        self._set_dict_(SmugAlbum.colorcorrections, 'ColorCorrection', newcolorcorrection)

    # FIXME: skip power setting "DefaultColor"
    # FIXME: skip power setting "ProofDays"
    # FIXME: skip power setting "Backprinting"
    # FIXME: skip power setting "UnsharpAmount"
    # FIXME: skip power setting "UnsharpRadius"
    # FIXME: skip power setting "UnsharpThreshold"
    # FIXME: skip power setting "UnsharpSigma"

    # Album CommunityID
    def get_communityid(self):
        """
        Get the album CommnityID attribute.
        """
        return self.album['Community']['id']
    def set_communityid(self, newcommunityid):
        """
        Set the album CommunityID attribute.
        """
        self._set_id_('CommunityID', newcommunityid)

    def list_images(self):
        """
        Return a list of SmugImage objects representing all of the images
        in this album.
        """
        images = []

        if self.get_imagecount() == 0:
            return images

        try:
            for image in self.sp.smugmug.images.get(self.session, self.get_id(), True, self.album['Key'])["Images"]:
                images.append(SmugImage(self.sp, self.session, image))
        except xmlrpclib.Fault, e:
            if str(e) == "<Fault 15: 'empty set - no images found'>":
                raise SmugException, "Internal error: album ImageCount was %d, but no images found" % self.album['ImageCount']
            raise
        return images

    def upload_image(self, filedata, filename=None, callback=None):
        """
        Upload a single image to this album from raw data.  On success,
        returns a SmugImage object.
        """
        # NOTE: while there is a call in the SmugMug API to upload an image,
        # it requires you to first base64 encode your image.  By doing the
        # upload "raw" as we do below, it's about 25% faster
        c = pycurl.Curl()
        c.setopt(c.URL, "https://upload.smugmug.com/photos/xmlrawadd.mg")
        c.setopt(c.USERAGENT, "smugapi(1.0)")
        c.response = cStringIO.StringIO()
        c.setopt(c.WRITEFUNCTION, c.response.write)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.UPLOAD, True)
        headers = [
            "X-Smug-Version: 1.2.0",
            "X-Smug-SessionID: " + self.session,
            "X-Smug-AlbumID: " + str(self.get_id()),
            "X-Smug-ResponseType: XML-RPC",
            ]
        if filename is not None:
            headers.append("X-Smug-Filename: " + filename)
        c.setopt(c.HTTPHEADER, [str(x) for x in headers])
        c.setopt(c.INFILESIZE, len(filedata))
        image = cStringIO.StringIO(filedata)
        c.setopt(c.READFUNCTION, image.read)

        if callback is not None:
            c.setopt(c.NOPROGRESS, 0)
            c.setopt(c.PROGRESSFUNCTION, callback)

        c.perform()
        response = c.getinfo(c.RESPONSE_CODE)
        result = c.response.getvalue()
        c.close()
        if response != 200:
            raise SmugException, "Error uploading %s: %d" % (filename, response)

        # FIXME: this is a hack.  For some reason doing a refresh of the
        # metadata (i.e. smugmug.albums.get()) doesn't refresh the ImageCount;
        # update it manually here
        self.album['ImageCount'] += 1
        # FIXME: Update LastUpdated as well?

        # Sometimes due to server load (or other things I'm not sure about),
        # we can't find the image that we just uploaded right away.  Try up
        # to 3 times here before throwing an exception
        count = 3
        while count > 0:
            for image in self.sp.smugmug.images.get(self.session, self.get_id(), True, self.get_key())["Images"]:
                if image['id'] == xmlrpclib.loads(result)[0][0]['Image']['id']:
                    return SmugImage(self.sp, self.session, image)
            count -= 1
        raise SmugException, "Could not find just uploaded image"

    def upload_image_from_file(self, filename, callback=None):
        """
        Upload a single image to this album from a file.  On success,
        returns a SmugImage object.
        """
        f = open(filename, "rb")
        filedata = f.read()
        f.close()

        return self.upload_image(filedata, filename, callback)

    def resort(self, sortby, direction):
        """
        Re-sort the images in this album.  The 'sortby' field has to be one
        of 'FileName', 'Caption', or 'DateTime', and the 'direction' field
        must be one of 'ASC' (for ascending) or 'DESC' (for descending).
        """
        sortfields = [ 'FileName,', 'Caption', 'DateTime' ]
        directionfields = [ 'ASC', 'DESC' ]
        if not sortby in sortfields:
            raise SmugException, "SortBy must be one of " + ', '.join([`num` for num in sortfields])
        if not direction in directionfields:
            raise SmugException, "Direction must be one of " + ', '.join([`num` for num in directionfields])
        self.sp.smugmug.albums.reSort(self.session, self.get_id(), sortby, direction)

    def delete(self):
        """
        Delete this album and all pictures associated with it. Once this
        method has been called, this album instance is invalid and
        should not be used.
        """
        self.sp.smugmug.albums.delete(self.session, self.get_id())

class SmugSubCategory:
    """
    This class represents a SubCategory in SmugMug.  Note that this class
    should never be instantiated directly; instead, the SmugCategory
    list subcategory method should be used, which will properly
    instantiate objects of this type.
    """
    def __init__(self, sp, session, metadata):
        self.sp = sp
        self.session = session
        self.metadata = metadata

    def __str__(self):
        return "%d:\t%s" % (self.get_id(), self.get_title())

    def get_id(self):
        """
        Get the SubCategory ID attribute.  This is the main identifier for
        this subcategory, and is unique across all subcategories in this
        category. This is a read-only attribute.
        """
        return self.metadata['id']

    def get_title(self):
        """
        Get the subcategory Title attribute.  This is an identifier for
        this subcategory, and is unique across all subcategories in this
        category.
        """
        return self.metadata['Title']
    def set_title(self, newname):
        """
        Set the subcategory Title attribute (string).
        """
        self.sp.smugmug.subcategories.rename(self.session, self.get_id(), newname)
        # Generally, I would prefer to refresh this from the server.  However,
        # in the case of a SubCategory, it only has two fields, so this is
        # sufficient
        self.metadata['Title'] = newname

    def delete(self):
        """
        Delete this subcategory.  Once this method has been called, this
        subcategory instance is invalid and should no longer be used.
        """
        self.sp.smugmug.subcategories.delete(self.session, self.get_id())

class SmugCategory:
    """
    This class represents a Category in SmugMug.  Note that this class
    should never be instantiated directly; instead, the SmugMug list
    category method should be used, which will properly instantiate objects
    of this type.
    """
    def __init__(self, sp, session, metadata):
        self.sp = sp
        self.session = session
        self.metadata = metadata

    def __str__(self):
        return "%d:\t%s" % (self.get_id(), self.get_title())

    def get_id(self):
        """
        Get the Category ID attribute.  This is the main identifier for
        this category, and is unique across all categories in your profile.
        This is a read-only attribute.
        """
        return self.metadata['id']

    def get_title(self):
        """
        Get the category Title attribute.  This is an identifier for
        this category, and is unique across all categories in your profile.
        """
        return self.metadata['Title']
    def set_title(self, newname):
        """
        Set the category Title attribute (string).
        """
        self.sp.smugmug.categories.rename(self.session, self.get_id(), newname)
        # Generally, I would prefer to refresh this from the server.  However,
        # in the case of a Category, it only has two fields, so this is
        # sufficient
        self.metadata['Title'] = newname

    def _get_subcategories_(self):
        try:
            subcategories = self.sp.smugmug.subcategories.get(self.session, self.get_id())['SubCategories']
        except xmlrpclib.Fault, e:
            if str(e) == "<Fault 15: 'empty set - no subcategories found'>":
                subcategories = []
            else:
                raise
        return subcategories

    def list_subcategories(self):
        """
        Return a list of SmugSubCategory objects representing all of the
        subcategories of this category.
        """
        subcategories = []

        for subcategory in self._get_subcategories_():
            subcategories.append(SmugSubCategory(self.sp, self.session, subcategory))
        return subcategories

    def create_subcategory(self, title):
        """
        Create a new subcategory with a title of "title".  Return a new
        SmugSubCategory object of the newly created subcategory.
        """
        subcategory = self.sp.smugmug.subcategories.create(self.session, title, self.get_id())
        newdict = { 'id': subcategory['SubCategory']['id'],
                    'Title': title }
        return SmugSubCategory(self.sp, self.session, newdict)

    def delete(self):
        """
        Delete this category.  Once this method has been called, this
        category instance is invalid and should no longer be used.
        """
        self.sp.smugmug.categories.delete(self.session, self.get_id())

class SmugMug:
    def __init__(self, username, password):
        self.key = "BDap2pxLv8MQQXZdfnzVQtJhRMCZ5MgM"
        self.username = username
        self.password = password
        self.sp = xmlrpclib.ServerProxy(_xmlrpcurl_)

    def login(self):
        """
        Login to the SmugMug account using the username and password from
        the instance instantiation.
        """
        rc = self.sp.smugmug.login.withPassword(self.username, self.password, self.key)
        self.session = rc["Session"]["id"]

    def _get_albums_(self):
        try:
            # NOTE: for xmlrpclib optional components, just keep appending
            # arguments
            albums = self.sp.smugmug.albums.get(self.session, "", True)["Albums"]
        except xmlrpclib.Fault, e:
            if str(e) == "<Fault 15: 'empty set - no albums found'>":
                albums = []
            else:
                raise

        return albums

    def list_albums(self):
        """
        Return a SmugAlbum object list of all albums in the gallery.
        """
        albums = []
        for album in self._get_albums_():
            albums.append(SmugAlbum(self.sp, self.session, album))
        return albums

    def create_album(self, title, category=0):
        """
        Create a new SmugMug album with Title 'title'.  Return a SmugAlbum
        object representing the new album.
        """
        thisalbum = self.sp.smugmug.albums.create(self.session, title, category)["Album"]

        # this is a bit heavyweight, but ensures that we are up-to-date with
        # the right information
        for album in self._get_albums_():
            if thisalbum['Key'] == album['Key'] and thisalbum['id'] == album['id']:
                return SmugAlbum(self.sp, self.session, album)

        raise SmugException, "Could not find just created album " + title

    def create_category(self, name):
        """
        Create a new SmugMug Category with 'name'.  Return a SmugCategory
        object representing the new category.
        """
        thiscategory = self.sp.smugmug.categories.create(self.session, name)
        newdict = { 'id': thiscategory['Category']['id'],
                    'Title': name }
        return SmugCategory(self.sp, self.session, newdict)

    def list_categories(self):
        """
        Return a SmugCategory object list of all of the categories in the
        gallery.
        """
        categories = []
        for category in self.sp.smugmug.categories.get(self.session)['Categories']:
            categories.append(SmugCategory(self.sp, self.session, category))
        return categories

    def logout(self):
        """
        Logout from the SmugMug instance.  Once this method has been called,
        this object is invalid and should no longer be used.
        """
        self.sp.smugmug.logout(self.session)
