import heapq

# WAND Top-K Algorithm
# By: Jaycent Gunawan Ongris (2106750231)
# Reference: Slide Kuliah

class WAND:
    def __init__(self, inv_index, k):
        self.inv_index = inv_index
        self.k = k
        self.pivot = 0
        self.result = []
        self.pointers_dict = {term_id: 0 for term_id in self.inv_index.keys()}
        self.threshold = 0
        self.cur_doc = 0
        self.fully_evaluated_docs = 0
    
    def sort(self):
        temp_curr_doc = {}
        for (term_id, pointer) in self.pointers_dict.items():
            curr_doc_id = self.inv_index[term_id][1][pointer][0]
            temp_curr_doc[term_id] = curr_doc_id 
        
        temp_curr_doc = [(term_id, curr_doc_id) for (term_id, curr_doc_id) in 
                         temp_curr_doc.items()]
        
        heapq.heapify(temp_curr_doc)
        
        sorted_by_doc_id = heapq.nsmallest(len(temp_curr_doc), temp_curr_doc, 
                                           key=lambda x: x[1])
        
        result = {}
        for (term_id, _) in sorted_by_doc_id:
            result[term_id] = self.inv_index[term_id]
        
        self.inv_index = result
    
    def find_pivot_term(self):
        accumulated_ub = 0
        for (term_id, info) in self.inv_index.items():
            accumulated_ub += info[0]
            if accumulated_ub >= self.threshold:
                return term_id
    
    def set_pivot(self):
        term_id = self.find_pivot_term()
        curr_pointer = self.pointers_dict[term_id]
        pivot = self.inv_index[term_id][1][curr_pointer][0]
        self.pivot = pivot
    
    def pick_term(self):
        # Simply mengambil term_id pertama saja
        for (term_id, _) in self.inv_index.items():
            return term_id
    
    def set_next_pointer(self, term_id, n):
        # Set pointer untuk term_id sedemikian hingga pointer tersebut menunjuk
        # elemen dengan doc_id >= n
        postings_list = self.inv_index[term_id][1]
        curr_pointer = self.pointers_dict[term_id]
        next_pointer = 0
        # Supaya lebih efisien, mulai dari current pointer saja
        for (index, (doc_id, _)) in enumerate(postings_list[curr_pointer:]):
            if doc_id >= n:
                 next_pointer = index + curr_pointer
                 break
        
        self.pointers_dict[term_id] = next_pointer
        
    def start_querying(self):
        while True:
            self.sort()
            self.set_pivot()
            if self.pivot == float('inf'):
                break
            if self.pivot <= self.cur_doc:
                aterm = self.pick_term()
                self.set_next_pointer(aterm, self.cur_doc + 1)
            else:
                # Get first term
                first_term = 0
                for (term_id, _) in self.inv_index.items():
                    first_term = term_id
                    break
                doc_id_pointed = self.inv_index[first_term][1][
                    self.pointers_dict[first_term]][0]
                if doc_id_pointed == self.pivot:
                    self.cur_doc = self.pivot
                    self.evaluate_document(self.cur_doc)
                    self.fully_evaluated_docs += 1
                else:
                    aterm = self.pick_term()
                    self.set_next_pointer(aterm, self.pivot)
        return self.result
    
    def evaluate_document(self, cur_doc):
        doc_score = 0
        for (term_id, pointer) in self.pointers_dict.items():
            doc_id, score = self.inv_index[term_id][1][pointer]
            if doc_id == cur_doc:
                doc_score += score
        
        temp_result = self.result
        temp_result.append((cur_doc, doc_score))
        heapq.heapify(temp_result)
        result = heapq.nlargest(self.k, temp_result, key=lambda x: x[1])
        
        if len(result) == self.k:
            # Update nilai threshold dengan score yang paling kecil
            self.threshold = result[-1][-1]
                
        self.result = result

def assert_test_case(k, expected, index):
    wand = WAND(index, k)
    assert wand.start_querying() == expected, "Output tidak sesuai"
    
# Format berupa dict {termID: (UB, [(docID, score)])}
# End of postings list ditandai dengan infinity agar ketika comparison diletakkan
# di paling bawah

if __name__ == '__main__':
    # term_id_map = {1: "hujan", 2: "turun", 3: "deras"}
    # Hanya mengambil term yang ada di query dan collection saja
    idx = {
           2: (1.8, [(1, 1.2), (6, 1.0), (7, 0.5), (10, 0.6), (11, 1.8), (float('inf'), None)]),
           3: (1.6, [(1, 1.5), (2, 0.4), (3, 0.6), (6, 1.0), (8, 1.5), (11, 1.6), (float('inf'), None)]),
           1: (1.5, [(1, 0.7), (3, 1.0), (6, 1.5), (8, 1.5), (10, 0.3), (12, 1.1), (float('inf'), None)]),
          }

    assert_test_case(1, [(6, 3.5)], idx)
    assert_test_case(2, [(6, 3.5), (1, 3.4000000000000004)], idx)
    assert_test_case(3, [(6, 3.5), (1, 3.4000000000000004), (11, 3.4000000000000004)], idx)
    
    wand = WAND(idx, 1)
    print(wand.start_querying())
    print(wand.fully_evaluated_docs)