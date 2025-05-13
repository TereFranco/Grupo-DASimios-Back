from django.urls import path
from .views import CategoryListCreate, CategoryRetrieveUpdateDestroy, AuctionListCreate, AuctionRetrieveUpdateDestroy, BidListCreate, BidRetrieveUpdateDestroy, UserAuctionListView, RatingListCreateView, RatingUpdateDeleteView, CommentListCreateView, CommentDetailView, UserCommentListView, UserRatingListView, WalletTransactionView, WalletBalanceView, CobrarSubastaView

app_name="auctions" 

urlpatterns = [ 
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'), 
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'), 
    path('', AuctionListCreate.as_view(), name='auction-list-create'), 
    path('<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'), 
    path('<int:auction_id>/bid/', BidListCreate.as_view(), name='bid-list-create'), 
    path('<int:auction_id>/bid/<int:pk>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'), 
    path('users/', UserAuctionListView.as_view(), name='action-from-users'), 
    path('<int:auction_id>/ratings/', RatingListCreateView.as_view(), name='rating-list-create'),
    path('<int:auction_id>/ratings/<int:pk>/', RatingUpdateDeleteView.as_view(), name='rating-update-delete'),
    path('<int:auction_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('user/comments/', UserCommentListView.as_view(), name='user-comments'),
    path('user/ratings/', UserRatingListView.as_view(), name='user-ratings'),
    path('wallet/', WalletTransactionView.as_view(), name='wallet-transactions'),
    path('wallet/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    #path('<int:auction_id>/cobrar/', CobrarSubastaView.as_view(), name='cobrar-subasta'),

    ] 