// Fetch the JSON data from the file
fetch('books.json')
  .then(response => response.json())
  .then(data => {
    // Get the container element to display book information
    const bookListContainer = document.getElementById('bookList');

    // Loop through the books and create HTML elements for each book
    data.forEach(book => {
      const bookDiv = document.createElement('div');
      bookDiv.classList.add('book');

      // Create an image element for the book thumbnail
      const img = document.createElement('img');
      img.src = book.thumbnailUrl;
      img.alt = book.title;
      img.classList.add('book-thumbnail');

      // Create elements for title, page count, and authors
      const title = document.createElement('h2');
      title.textContent = book.title;

      const pageCount = document.createElement('p');
      pageCount.textContent = `Page Count: ${book.pageCount}`;

      const authors = document.createElement('p');
      authors.textContent = `Authors: ${book.authors.join(', ')}`;

      // Append elements to the bookDiv
      bookDiv.appendChild(img);
      bookDiv.appendChild(title);
      bookDiv.appendChild(pageCount);
      bookDiv.appendChild(authors);

      // Append the bookDiv to the bookListContainer
      bookListContainer.appendChild(bookDiv);
    });
  })
  .catch(error => {
    console.error('Error fetching data:', error);
  });
