EPYDOC=epydoc  
DSTDOC=docstrings  
  
target:
	$(EPYDOC) --html --graph=all -v -o $(DSTDOC) danmaku/*.py  
  
clean:
	rm -rf $(DSTDOC)  

