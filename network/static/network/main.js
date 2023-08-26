document.addEventListener('DOMContentLoaded', function() {
    
   


    document.querySelectorAll('.like-btn').forEach( likeBtn => {
        likeBtn.addEventListener('click', likeFunc)
    })
    
  });

function likeFunc(event) {
const clickedPostContainer = event.target.closest('.post-container');
const postId = clickedPostContainer.getAttribute('postid');



fetch(`/toggle-like/${postId}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken, // Include the CSRF token in the headers
    }
})
.then(response => response.json())
.then(data => {
    // Update the like count and button text based on the response from the server.
    clickedPostContainer.querySelector('.post-likes').innerHTML = data.likes;
    clickedPostContainer.querySelector('.like-btn').innerHTML = data.liked ? "Like" : "Unlike";
});
}
