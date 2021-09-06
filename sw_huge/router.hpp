/**
 * router.hpp
 *
 * for Vivado HLS
 */

#ifndef __ROUTER_HPP__
#define __ROUTER_HPP__

#ifdef SOFTWARE
#include "ap_int.h"
#else
#include <ap_int.h>
#endif

//#define DEBUG_PRINT  // ���낢��\������
#define USE_ASTAR    // A* �T�����g��
#define USE_MOD_CALC // �^�[�Q�b�g���C���̑I���ɏ�]���Z��p����

using namespace std;


// �e��ݒ�l
#define MAX_WIDTH   72      // X, Y �̍ő�l (7�r�b�g�Ŏ��܂�)
#define BITWIDTH_XY 13
#define BITMASK_XY  65528   // 1111 1111 1111 1000
#define MAX_LAYER   8       // Z �̍ő�l (3�r�b�g)
#define BITWIDTH_Z  3
#define BITMASK_Z   7       // 0000 0000 0000 0111

#define MAX_CELLS  41472    // �Z���̑��� =72*72*8 (16�r�b�g�Ŏ��܂�)
#define MAX_LINES  65535      // ���C�����̍ő�l (7�r�b�g)
#define MAX_PATH   256      // 1�̃��C�����Ή�����Z�����̍ő�l (8�r�b�g)
#define MAX_PQ     4096     // �T�����̃v���C�I���e�B�E�L���[�̍ő�T�C�Y (12�r�b�g) ����Ȃ������H

#define PQ_PRIORITY_WIDTH 16
#define PQ_PRIORITY_MASK  65535       // 0000 0000 0000 0000 1111 1111 1111 1111
#define PQ_DATA_WIDTH     16
#define PQ_DATA_MASK      4294901760  // 1111 1111 1111 1111 0000 0000 0000 0000

#define MAX_WEIGHT 255      // �d�݂̍ő�l (8�r�b�g�Ŏ��܂�)
#define BOARDSTR_SIZE 262144 // �{�[�h�X�g�����O�̍ő啶���� (�Z���� 72*72*8 ����Ηǂ�)


void lfsr_random_init(ap_uint<32> seed);
ap_uint<32> lfsr_random();
//ap_uint<32> lfsr_random_uint32(ap_uint<32> a, ap_uint<32> b);
//ap_uint<32> lfsr_random_uint32_0(ap_uint<32> b);

unsigned int new_weight(unsigned int x);
bool pynqrouter(unsigned int boardstr[BOARDSTR_SIZE], ap_uint<32> seed, ap_int<32> *status);

#ifdef USE_ASTAR
unsigned int abs_uint7(unsigned int a, unsigned int b);
unsigned int abs_uint3(unsigned int a, unsigned int b);
#endif

void search(unsigned int *path_size, unsigned int path[MAX_PATH], unsigned int start, unsigned int goal, unsigned int w[MAX_WEIGHT]);
void pq_push(unsigned int priority, unsigned int data, unsigned int *pq_len, ap_uint<32> pq_nodes[MAX_PQ]);
void pq_pop(unsigned int *ret_priority, unsigned int *ret_data, unsigned int *pq_len, ap_uint<32> pq_nodes[MAX_PQ]);

#endif /* __ROUTER_HPP__ */
