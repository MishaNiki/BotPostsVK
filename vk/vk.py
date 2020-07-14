import requests
import datetime
import re



class Post:
    """
        VKontakte post object containing text and image links
    """
    def __init__(self, text, date):
        self.text = text
        self.date = date
        self.photos = []
        self.link = ''
        self.video = ''


class VK:
    """
        VK object implements work with VK API
    """
    def __init__(self, token):
        self.token = token


    def check_by_uuid(self, uuid):
        """
            Check uuid community VKontakte

            if the community exists then returns its id
            otherwise returns a negative code
        """

        # community unique name verification request
        r = requests.get('https://api.vk.com/method/utils.resolveScreenName',
                         params={'screen_name': uuid, 'access_token': self.token, 'v': '5.120'})

        if r.json()['response'] == []:
            return -1
        elif r.json()['response']['type']!= 'group':
            return -2
        else: return r.json()['response']['object_id'] # returning id community


    def get_posts_by_id(self, id, count):
        """
            get community posts vk
            count - number of recent posts
        """

        if count > 25: count = 25 # limit

        # getting community posts and information about him
        r = requests.get('https://api.vk.com/method/wall.get',
                         params={'owner_id': '-'+str(id), 'count': count, 'filter': 'owner', 'extended':1,
                                 'access_token': self.token, 'v': '5.52'})

        # list object Post
        posts = []

        for item in r.json()['response']['items']:

            # creating post
            # add data and text
            post = Post(item['text'], datetime.datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S'))
            if item.get('attachments') is not None:
                for attac in item['attachments']:

                    # selection of the largest image
                    if attac['type'] == 'photo':
                        max = 0
                        max_url = ''
                        for key, value in attac['photo'].items():
                            temp = re.findall(r'photo_(\d+)', key) # get size photo
                            if len(temp) != 0 and int(temp[0]) > max:
                                max = int(temp[0])
                                max_url = value
                        post.photos.append(max_url) # add largest image

                    elif attac['type'] == "link":
                        post.link = attac['link']['url']
                    elif attac['type'] == "video" :
                        vk_video = requests.get('https://api.vk.com/method/video.get',
                                     params={'owner_id': '{}_{}'\
                                                .format(
                                                         attac['video']['owner_id'],
                                                         attac['video']['id']
                                            ),
                                             'access_token': self.token,
                                             'v': '5.52'})
                        post.video = vk_video.json()['response']['items'][0]['player']

            posts.append(post)

        return posts, r.json()['response']['groups'][0]['name']