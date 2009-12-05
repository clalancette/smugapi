#!/usr/bin/python

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

import smugapi
import getopt
import sys

def test_change_attribute(obj, name, newval):
    getmethodname = 'get_' + name.lower()
    setmethodname = 'set_' + name.lower()

    if not getattr(obj, getmethodname):
        print "Test logic error; no get method %s FAIL" % getmethodname
        return
    if not getattr(obj, setmethodname):
        print "Test logic error; no set method %s FAIL" % setmethodname
        return
    # get the current value
    origval = getattr(obj, getmethodname)()
    #print "\t%s: %s" % (name, origval)
    if origval == newval:
        print "Test logic error; original value %s is the same as new value %s" % (origval, newval)
        return
    # try to change to an invalid value
    try:
        # FIXME: for the string types (Password, PasswordHint, Description,
        # CommunityID, CategoryID, Caption), we need an invalid value that
        # is not a string
        getattr(obj, setmethodname)('foo')
        print "No exception for invalid %s FAIL" % name
    except smugapi.SmugException:
        print "Saw exception for invalid %s PASS" % name
    # change it
    getattr(obj, setmethodname)(newval)
    # check to see that the change stuck
    newval = getattr(obj, getmethodname)()
    if origval == newval:
        print "Changing attribute %s: oldval didn't change FAIL" % name
        return
    getattr(obj, setmethodname)(origval)
    newval = getattr(obj, getmethodname)()
    if origval != newval:
        print "Restoring attribute %s FAIL" % name
    else:
        print "Changing attribute %s PASS" % name

def test_get_attribute(obj, name):
    getmethodname = 'get_' + name.lower()

    if not getattr(obj, getmethodname):
        print "Test logic error; no get method %s FAIL" % getmethodname
        return

    if getattr(obj, getmethodname)() != None:
        print "Getting attribute %s PASS" % name
    else:
        print "Getting attribute %s FAIL" % name

# main
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'l:p:', ['login=', 'password='])
except getopt.GetoptError, err:
    print str(err)
    print "Usage: %s [--login=username] [--password=password]" % sys.argv[0]
    sys.exit(1)

username = None
password = None
for o, a in opts:
    if o in ("-l", "--login"):
        username = a
    elif o in ("-p", "--password"):
        password = a
    else:
        assert False, "unhandled option"

if username is None or password is None:
    print "--login and --password are required"
    sys.exit(2)

# main test
try:
    test = smugapi.SmugMug('foo', 'bar')
    test.login()
    print "No exception for invalid user/password FAIL"
except:
    print "Invalid user/login exception PASS"

test = smugapi.SmugMug(username, password)
try:
    test.login()
except Exception,e:
    # we have no choice but to abort if this failed
    print e
    print "Login FAIL"
    sys.exit(1)
print "Login PASS"

# test category list
travelcat = None
for category in test.list_categories():
    if category.get_title() == "Travel":
        travelcat = category
        break
if travelcat is None:
    print "Category find by title FAIL"
else:
    print "Category find by title PASS"
# test create_category
try:
    for category in test.list_categories():
        if category.get_title() == "testcat":
            category.delete()
except:
    pass
newcat = test.create_category('testcat')
print "Create category PASS"
# test duplicate category
try:
    newcat = test.create_category('testcat')
    print "Duplicate category title FAIL"
except:
    print "Duplicate category title PASS"
# test category rename
newcat.set_title('testrename')
tmp = None
for category in test.list_categories():
    if category.get_title() == "testrename":
        tmp = category
        break
if tmp is None:
    print "Finding renamed category FAIL"
else:
    print "Finding renamed category PASS"
newcat.set_title('testcat')

# test subcategory create
try:
    for subcat in newcat.list_subcategories():
        if subcat.get_title() == 'testsub':
            subcat.delete()
except:
    pass
newsub = newcat.create_subcategory('testsub')
print "Create subcategory PASS"
# test duplicate subcategory
try:
    newsub.create_subcategory('testsub')
    print "Duplicate subcategory title FAIL"
except:
    print "Duplicate subcategory title PASS"
# test subcategory rename
newsub.set_title('testsubrename')
tmp = None
for subcat in newcat.list_subcategories():
    if subcat.get_title() == "testsubrename":
        tmp = subcat
        break
if tmp is None:
    print "Finding renamed subcategory FAIL"
else:
    print "Finding renamed subcategory PASS"
newsub.set_title('testsub')

newsub.delete()
try:
    newsub.delete()
    print "Delete invalid subcategory FAIL"
except:
    print "Delete invalid subcategory PASS"

newcat.delete()
try:
    newcat.delete()
    print "Delete invalid category FAIL"
except:
    print "Delete invalid category PASS"

# test album creation
try:
    for album in test.list_categories():
        if album.get_title() == "testalbum":
            album.delete()
except Exception, e:
    pass

newalbum = test.create_album('testalbum')
print "Create new album PASS"
pic1 = newalbum.upload_image_from_file('101_6145_by_iz.mendoza.jpg')
print "Upload image PASS"
pic2 = newalbum.upload_image_from_file('londres_subway_by_maccosta.jpg')
# unchangeable fields
if newalbum.get_imagecount() == 2:
    print "ImageCount is correct PASS"
else:
    print "ImageCount expect to be 2, but was actually %d FAIL" % newalbum.get_imagecount()
test_get_attribute(newalbum, 'id')
test_get_attribute(newalbum, 'Title')
test_get_attribute(newalbum, 'Key')
test_get_attribute(newalbum, 'LastUpdated')
# test changing booleans
test_change_attribute(newalbum, 'Printable', False)
test_change_attribute(newalbum, 'FriendEdit', True)
test_change_attribute(newalbum, 'FamilyEdit', True)
test_change_attribute(newalbum, 'WorldSearchable', False)
test_change_attribute(newalbum, 'SmugSearchable', False)
test_change_attribute(newalbum, 'CanRank', False)
test_change_attribute(newalbum, 'Comments', False)
test_change_attribute(newalbum, 'External', False)
test_change_attribute(newalbum, 'HideOwner', True)
test_change_attribute(newalbum, 'Clean', True)
test_change_attribute(newalbum, 'EXIF', False)
test_change_attribute(newalbum, 'Share', False)
test_change_attribute(newalbum, 'Public', False)
test_change_attribute(newalbum, 'SquareThumbs', False)
test_change_attribute(newalbum, 'Filenames', True)
test_change_attribute(newalbum, 'X2Larges', False)
test_change_attribute(newalbum, 'X3Larges', False)
test_change_attribute(newalbum, 'Originals', False)
test_change_attribute(newalbum, 'Geography', False)
# test changing strings
test_change_attribute(newalbum, 'Password', 'testpass')
test_change_attribute(newalbum, 'PasswordHint', 'testhint')
test_change_attribute(newalbum, 'Description', 'Test Description')
# test changing ID's
test_change_attribute(newalbum, 'CommunityID', 67)
try:
    for cat in test.list_categories():
        if cat.get_title() == 'testattr':
            cat.delete()
except Exception, e:
    pass
tmpcat = test.create_category('testattr')
tmpsubcat = tmpcat.create_subcategory('testsubattr')
test_change_attribute(newalbum, 'CategoryID', tmpcat.get_id())
test_change_attribute(newalbum, 'SubCategoryID', tmpsubcat.get_id())
tmpsubcat.delete()
tmpcat.delete()

# FIXME: I don't know what HighlightID is, or how I should implement it
#test_change_attribute(newalbum, 'HighlightID', 20)
# test changing fixed values
test_change_attribute(newalbum, 'SortMethod', 'Date')
test_change_attribute(newalbum, 'SortDirection', 'Descending')
test_change_attribute(newalbum, 'ColorCorrection', 'Yes')
test_change_attribute(newalbum, 'TemplateID', 'Traditional')
test_change_attribute(newalbum, 'Position', 2)
# test changing a list
test_change_attribute(newalbum, 'Keywords', ['Test', 'Keywords'])

# test getting image attributes
test_get_attribute(pic1, 'id')
test_get_attribute(pic1, 'Key')
test_get_attribute(pic1, 'AlbumKey')
test_get_attribute(pic1, 'FileName')
test_get_attribute(pic1, 'Date')
test_get_attribute(pic1, 'Format')
test_get_attribute(pic1, 'Serial')
test_get_attribute(pic1, 'Size')
test_get_attribute(pic1, 'Width')
test_get_attribute(pic1, 'Height')
test_get_attribute(pic1, 'MD5Sum')
test_get_attribute(pic1, 'LastUpdated')
test_get_attribute(pic1, 'AlbumURL')
test_get_attribute(pic1, 'TinyURL')
test_get_attribute(pic1, 'ThumbURL')
test_get_attribute(pic1, 'SmallURL')
test_get_attribute(pic1, 'MediumURL')
test_get_attribute(pic1, 'LargeURL')
test_get_attribute(pic1, 'XLargeURL')
test_get_attribute(pic1, 'X2LargeURL')
test_get_attribute(pic1, 'X3LargeURL')
test_get_attribute(pic1, 'OriginalURL')
test_get_attribute(pic1, 'EXIF')
# FIXME: these three are listed as "if available", but don't seem to
# be available in the pictures I'm looking at.  Maybe need EXIF data or
# something
#test_get_attribute(pic1, 'Latitude')
#test_get_attribute(pic1, 'Longitude')
#test_get_attribute(pic1, 'Altitude')
# test changing image attributes
test_change_attribute(pic1, 'Caption', 'hello')
test_change_attribute(pic1, 'Keywords', ['Test', 'Keywords'])
test_change_attribute(pic1, 'Hidden', True)
# FIXME: changing position doesn't seem to work, I keep getting system error
#test_change_attribute(pic1, 'Position', 2)
try:
    for album in test.list_albums():
        if album.get_title() == 'testalbum2':
            album.delete()
except Exception, e:
    pass
newalbum2 = test.create_album('testalbum2')
origid = pic1.get_albumid()
pic1.set_albumid(newalbum2.get_id(), newalbum2.get_key())
if origid == pic1.get_albumid():
    print "Same albumid changing from new to old FAIL"
else:
    print "Change albumid PASS"

pic1id = pic1.get_id()
pic1.delete()
saw = False
for image in newalbum2.list_images():
    if image.get_id() == pic1id:
        saw = True
        break
if saw:
    print "Saw deleted image pic1 FAIL"
else:
    print "Didn't see deleted image pic1 PASS"

# FIXME: add formal test for album delete
# FIXME: add test for album.list_images()
# FIXME: add test for conn.list_albums()
# FIXME: add test for progress for image upload/download

newalbum2.delete()

newalbum.delete()

test.logout()
