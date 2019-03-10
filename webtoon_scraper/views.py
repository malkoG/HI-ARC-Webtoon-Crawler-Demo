from django.http import Http404

from django.shortcuts import render, get_object_or_404, \
                                get_list_or_404, redirect


from .models import Favorite, Episode
from .utils import Crawler

# Create your views here.
def webtoon_index(request):
    if request.method == 'POST':
        webtoon_title = request.POST.get('webtoon')

        try:
            webtoon = get_object_or_404(Favorite, title=webtoon_title)
        except:
            raise Http404("해당 웹툰이 존재하지 않습니다.")

        webtoon_url = webtoon.url 
        webtoon_service = webtoon.service

        existing_episode_list = Episode.objects \
                                        .filter(webtoon=webtoon) \
                                        .order_by('-created_at')
                                            
        crawler = Crawler(webtoon_url, webtoon_service)

        episodes = []
        for episode in existing_episode_list:
            e = {
                'title': episode.title,
                'url': episode.url
            }
            episodes.append(e)

        fetched_episodes = crawler.crawl()

        result = []
        for episode_for_check in fetched_episodes:
            if episode_for_check not in episodes:
                result.append(episode_for_check)
            
        for episode in result:
            Episode.objects.create(title=episode['title'], url=episode['url'], webtoon=webtoon)

        return redirect('webtoon_index')

    options = [] 
    for w in Favorite.objects.all():
        options.append(w.title)

    episode_list = Episode.objects.all()

    data = {
        'options': options,
        'episode_list': episode_list
    }

    return render(request, 
                'webtoon_scraper/webtoon_list_index.html', data)
