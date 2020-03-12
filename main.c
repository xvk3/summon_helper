#include <stdio.h>
#include <string.h>

#define MAX_NAME_LENGTH 32

typedef unsigned int bool;

typedef struct DLINKED_LIST {
  struct _DLINKED_LIST *pPrev;
  struct _DLINKED_LIST *pNext;
} DLINKED_LIST;

typedef struct PLAYER {
  DLINKED_LIST Header;
  char *Player;
  unsigned int *Fights;
  unsigned int *Wins;
  unsigned int *Losses;
} PLAYER;

// Pointer to the player who was summoned last
struct PLAYER* Last;

// Function Declarations
void* forEachElement(PLAYER* Start, void (*func)(struct PLAYER*));
char* handleInput();
struct PLAYER* lookupPlayer(char* player);
void printSummonOrder(struct PLAYER* pCurrent);
void printElementContent(struct PLAYER* pCurrent);
bool insertElementBefore(struct PLAYER* pCurrent, struct PLAYER* pNew);
bool insertElementAfter(struct PLAYER* pCurrent, struct PLAYER* pNew);  // Could be implemented as a wrapper for 'insertElementBefore'
bool removeElement(struct PLAYER* pCurrent);
bool swapTwoElements(struct PLAYER* pSwapFirst, struct PLAYER* pSwapSecond);
bool moveElementAfter(struct PLAYER* pToMove, struct PLAYER* pStatic);

// Function Definitions
void* forEachElement(PLAYER* Start, void (*func)(struct PLAYER*)) {

  if(!Start) Start = Last;
  PLAYER* pWorking = Start;
  do {
    func(pWorking);
    pWorking = pWorking->Header.pNext;
  } while(pWorking != Start);
  
  return 0;
}

char* handleInput() {

  printf("Who has just been summoned? : ");

  // Removing newline character from input string
  char* input = (char*)malloc(MAX_NAME_LENGTH);
  fgets(input, MAX_NAME_LENGTH, stdin);
  if(input[strlen(input)-1] == '\n') {
    input[strlen(input)-1] = '\0';
  }

  // Debug Functions
  if(input[0] == '#') {
    forEachElement(Last, printElementContent);
    printf("Special Function #\n");
    return 0;
  }
  if(input[0] == 'L') {
    printElementContent(Last);
    return 0;
  }
  
  // Use return value to choose between restarting the while(1) loop or continuing
  return input;
}

PLAYER* lookupPlayer(char* player) {

  PLAYER* pWorking = Last;

  do {
    if(!strcmp(player, pWorking->Player)) return pWorking;
    pWorking = pWorking->Header.pNext;
  } while(pWorking != Last);

  return 0;
}

void printSummonOrder(struct PLAYER* pCurrent) {

  signed int short order = 1;
  PLAYER* pWorking = pCurrent->Header.pNext;
  PLAYER* pHolding = pWorking;
  do {
    printf("[%d] - %s\n", order, pWorking->Player);
    pWorking = pWorking->Header.pNext;
    order++;
  } while(pWorking != pHolding);

  return;
}

void printElementContent(struct PLAYER* pCurrent) {

  // TODO tidy this function
  printf("------\n");
  printf("%s Element\n", pCurrent->Player);
  PLAYER* pNext = pCurrent->Header.pNext;
  printf("pNext = %s\n", pNext->Player);
  PLAYER* pPrev = pCurrent->Header.pPrev;
  printf("pPrev = %s\n", pPrev->Player);
  printf("Fights = %d\n", pCurrent->Fights);
  printf("Wins   = %d\n", pCurrent->Wins);
  printf("Losses = %d\n", pCurrent->Losses);
  printf("------\n");
  return;
}

bool insertElementBefore(struct PLAYER* pCurrent, struct PLAYER* pNew) {
  
  // Get the pointer to the previous element
  PLAYER* pBefore = (PLAYER*)pCurrent->Header.pPrev;

  // Update element before pCurrent (pBefore) to have it's pNext point to pNew
  pBefore->Header.pNext = pNew;

  // Update pNew to have it's pPrev point to pBefore
  pNew->Header.pPrev = pBefore;

  // Update pNew to have it's pNext point to pCurrent
  pNew->Header.pNext = pCurrent;

  // Finally update pCurrent to have it's pPrev point to pNew
  pCurrent->Header.pPrev = pNew;

  return 1;
}

bool insertElementAfter(struct PLAYER* pCurrent, struct PLAYER* pNew) {

  // Get the pointer to the following element
  PLAYER* pAfter = (PLAYER*)pCurrent->Header.pNext;

  // Update element after pCurrent (pAfter) to have it's pPrev point to pNew
  pAfter->Header.pPrev = pNew;

  // Update pNew to have it's pNext point to pAfter
  pNew->Header.pNext = pAfter;

  // Update pNew to have it's pPrev point to pCurrent
  pNew->Header.pPrev = pCurrent;

  // Finally update pCurrent to have it's pNext point to pNew
  pCurrent->Header.pNext = pNew;

  return 1;
}

bool removeElement(struct PLAYER* pCurrent) {

  PLAYER* pNext = (PLAYER*)pCurrent->Header.pNext;
  PLAYER* pPrev = (PLAYER*)pCurrent->Header.pPrev;

  // Update pPrev's pNext to be pNext
  pPrev->Header.pNext = pNext;
  
  // Likewise update pNext's pPrev to be pPrev (removing references to pCurrent from surrounding elements)
  pNext->Header.pPrev = pPrev;

  return 1;
}

bool swapTwoElements(struct PLAYER* pSwapFirst, struct PLAYER* pSwapSecond) {

  // Is the first element BEFORE and ADJACENT to the second?
  if(pSwapFirst->Header.pPrev == pSwapSecond) {
    pSwapFirst->Header.pNext = pSwapSecond->Header.pNext;   // Updates pSwapFirst's pNext to be pSwapSecond's pNext
    pSwapFirst->Header.pPrev = pSwapSecond;
    pSwapSecond->Header.pPrev = pSwapFirst->Header.pPrev;   // Updates pSwapSecond's pPrev to be pSwapFirst's pPrev
    pSwapSecond->Header.pNext = pSwapFirst;
    return 1;
  }
  // Is the first element AFTER and ADJACENT to the second?
  if (pSwapFirst->Header.pNext == pSwapSecond) {
    pSwapFirst->Header.pPrev = pSwapSecond->Header.pPrev;  // Updates pSwapFirst's pPrev to be pSwapSeconds's pPrev
    pSwapFirst->Header.pNext = pSwapSecond;
    pSwapSecond->Header.pNext = pSwapFirst->Header.pPrev;   // Updates pSwapSeconds's pNext to be pSwapFirst's pNext
    pSwapSecond->Header.pPrev = pSwapFirst;
    return 1;
  }

  // Update (pSwapFirst->Header.pPrev)->Header.pNext to point to pSwapSecond
  PLAYER* pBeforeSwapFirst = pSwapFirst->Header.pPrev;
  pBeforeSwapFirst->Header.pNext = pSwapSecond;
  // Update (pSwapFirst->Header.pNext)->Header.pPrev to point to pSwapSecond
  PLAYER* pAfterSwapFirst = pSwapFirst->Header.pNext;
  pAfterSwapFirst->Header.pPrev = pSwapSecond;
  // Update (pSwapSecond->Header.pPrev)->Header.pNext to point to pSwapFirst
  PLAYER* pBeforeSwapSecond = pSwapSecond->Header.pPrev;
  pBeforeSwapSecond->Header.pNext = pSwapFirst;
  // Update (pSwapSecond->Header.pNext)->Header.pPrev to point to pSwapFirst
  PLAYER* pAfterSwapSecond = pSwapSecond->Header.pNext;
  pAfterSwapSecond->Header.pPrev = pSwapFirst;

  return 1;
}

bool moveElementAfter(struct PLAYER* pToMove, struct PLAYER* pStatic) {

  // Step 1: Update pStatic->Header.pNext to point to pToMove
  PLAYER* pOriginalAfterStatic = pStatic->Header.pNext;
  pStatic->Header.pNext = pToMove;
  // Step 2: Update pOriginalAfterStatuc->Header.pPrev to point to pToMove
  pOriginalAfterStatic->Header.pPrev = pToMove;
  // Info: This has inserted pToMove after pStatic and before pOriginalAfterStatic (from the perspective on pStatic and pOriginalAfterStatic)
  // Step 3: Stitch up the elements before and after pToMove's original position
  PLAYER* pBeforeToMove = pToMove->Header.pPrev;
  PLAYER* pAfterToMove  = pToMove->Header.pNext;
  pBeforeToMove->Header.pNext = pAfterToMove;
  pAfterToMove->Header.pPrev = pBeforeToMove;
  // Step 4: Finally update the Header for pToMove
  pToMove->Header.pPrev = pStatic;
  pToMove->Header.pNext = pOriginalAfterStatic;

  return 0;
}

int main() {

  printf("Summon Cycles\n");

  char* first = handleInput();
  if(!first) return -1;
  
  // Build first element for doubly linked list
  PLAYER *Head = (PLAYER*)malloc(sizeof(PLAYER));
  Head->Header.pPrev = Head;
  Head->Header.pNext = Head;
  Head->Player = (char*)malloc(strlen(first));
  strcpy(Head->Player, first);

  printSummonOrder(Head);

  // Initialise the pointer to the last USED element
  Last = Head;

  while(1) {

    char* input = handleInput();
    if(!input) continue;

    PLAYER* Exists = lookupPlayer(input);
    if(Exists) {
      if(Last->Header.pNext == Exists) {
        // Summoned in the correct order
      } else {
        printf("%s jumped the queue\n", Exists->Player);
        moveElementAfter(Exists, Last);
      }
      Exists->Fights += 1;
      Last = Exists;  // Important to update this
      printSummonOrder(Last);
      continue;
    }

    // Create new player element
    PLAYER *New = (PLAYER*)malloc(sizeof(PLAYER));
    // Initialise Player identifier
    New->Player = (char*)malloc(strlen(input)+1);
    strcpy(New->Player, input);
    // Initialise defaults
    New->Fights = 0;
    New->Wins   = 0;
    New->Losses = 0;
    // Insert player into linked last (after most recent element)
    insertElementAfter(Last, New);
    //printLinkedList(Head);
    printSummonOrder(New);
    // Set the Last element to the newly added one
    Last = New;
    //funcForEachElement(Last, printElementContent);
  }
  return 1;
}
