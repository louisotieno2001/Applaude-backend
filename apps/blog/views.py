from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

class PostListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating posts.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Optimize queryset to prevent N+1 queries by selecting the related author.
        """
        return Post.objects.select_related('author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a single post.
    """
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Optimize queryset to prevent N+1 queries by selecting the related author.
        """
        return Post.objects.select_related('author').all()

class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating comments for a post.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Optimize queryset to prevent N+1 queries by selecting related post and author.
        """
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.select_related('post', 'author').filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        post = Post.objects.get(pk=post_id)
        serializer.save(author=self.request.user, post=post)

class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a single comment.
    """
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        Optimize queryset to prevent N+1 queries by selecting related post and author.
        """
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.select_related('post', 'author').filter(post_id=post_id)
