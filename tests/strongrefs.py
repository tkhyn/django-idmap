from .app.models import Category, Article
from .weakrefs import IdMapWeakRefsTests


class IdMapStrongRefsTests(IdMapWeakRefsTests):
    # derives from tests with weak refs
    # all tests should pass except CachedToRegular, where the expected
    # result is the contrary

    @classmethod
    def setUpClass(cls):
        Category.use_strong_refs = True
        Article.use_strong_refs = True
        super(IdMapStrongRefsTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(IdMapStrongRefsTests, cls).tearDownClass()
        # restore defaults
        Category.use_strong_refs = False
        Article.use_strong_refs = False

    def test_cached_to_regular(self):
        # overrides a test in IdMapWeakRefsTests
        # the expected result is that the category objects are the same
        # indeed, the reference to the articles is not weak anymore and they
        # are kept in memory after setUp. They are only erased when calling
        # flush

        article_list = Article.objects.all().select_related('category')
        last_article = article_list[0]
        for article in article_list[1:]:
            self.assertIs(article.category2, last_article.category2)
            last_article = article
